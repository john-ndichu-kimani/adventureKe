import json
import requests
import logging
from django.conf import settings
from django.db import transaction
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt

from adventureApp.models import Tour, Booking, Payment
from adventureApp.forms import BookingForm, TourSearchForm
from .mpesa_utils import (
    get_mpesa_access_token,
    validate_phone_number,
    generate_mpesa_password,
    MPesaError
)


# Create your views here.

@login_required
def user_dashboard(request):
    # Search functionality
    search_form = TourSearchForm(request.GET)
    tours_query = Tour.objects.filter(is_active=True)

    if search_form.is_valid():
        query = search_form.cleaned_data.get('query')
        if query:
            tours_query = tours_query.filter(
                Q(title__icontains=query) |
                Q(destination__name__icontains=query) |
                Q(description__icontains=query)
            )

    # Pagination
    paginator = Paginator(tours_query, 6)  # 6 tours per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'tours': page_obj,
        'search_form': search_form,
        'total_tours': tours_query.count(),
    }
    return render(request, 'user_dashboard.html', context)


@login_required
@transaction.atomic
def book_tour(request, tour_id):
    if not request.user.is_authenticated:
        return redirect('login')
    tour = get_object_or_404(Tour, id=tour_id)


    if tour.available_slots <= 0:
        messages.error(request, "This tour is fully booked.",extra_tags='book')
        return redirect('user-dashboard')
    # Lock tour row
    tour.refresh_from_db()

    if request.method == 'POST':
        form = BookingForm(request.POST, tour=tour, user=request.user)
        if form.is_valid():
            try:
                booking = form.save()
                messages.success(request,"Successfully booked the tour",extra_tags='book')
                return redirect('my-bookings')
            except Exception as e:
                messages.error(request, f"Booking failed: {str(e)}")
    else:
        form = BookingForm(tour=tour, user=request.user)

    context = {
        'form': form,
        'tour': tour,
    }
    return render(request, 'book_package.html', context)


@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user, is_active=True)

    if request.method == 'POST':
        booking_id = request.POST.get('booking_id')
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)

        if 'cancel' in request.POST:
            # Check if booking can be cancelled
            if booking.status in ['PENDING', 'CONFIRMED']:
                booking.status = 'CANCELLED'
                booking.is_active = False
                booking.save()

                # Optional: Increment available slots back to the tour
                booking.tour.available_slots += booking.slots_booked
                booking.tour.save()

                messages.success(request, "Booking has been cancelled.",extra_tags='my-bookings')

        elif 'confirm' in request.POST:
            # Only allow confirmation of pending bookings
            if booking.status == 'PENDING':
                # Check tour availability
                if booking.tour.is_available() and booking.slots_booked <= booking.tour.available_slots:
                    booking.status = 'CONFIRMED'

                    # Reduce available slots
                    booking.tour.available_slots -= booking.slots_booked
                    booking.tour.save()

                    booking.save()

                    # Redirect to payment page
                    return redirect('initiate_payment', booking_id=booking.id)
                else:
                    messages.error(request, "Tour is not available or insufficient slots.",extra_tags='my-bookings')
            else:
                messages.error(request, "This booking cannot be confirmed.",extra_tags='my-bookings')

    context = {'bookings': bookings}
    return render(request, 'my_bookings.html', context)


@login_required
def initiate_payment(request, booking_id):
    """
    Initiate MPesa STK Push for payment
    """
    try:
        # Retrieve booking and validate
        booking = get_object_or_404(
            Booking,
            id=booking_id,
            user=request.user,
            status='CONFIRMED'
        )

        # Validate phone number
        phone_number = validate_phone_number(request.user.phone_number)

        # Get access token
        access_token = get_mpesa_access_token()

        # Generate password
        mpesa_credentials = generate_mpesa_password()

        # Prepare STK Push payload
        payload = {
            "BusinessShortCode": settings.MPESA_BUSINESS_SHORTCODE,
            "Password": mpesa_credentials['password'],
            "Timestamp": mpesa_credentials['timestamp'],
            "TransactionType": "CustomerPayBillOnline",
            "Amount": str(int(booking.total_price)),
            "PartyA": phone_number,
            "PartyB": settings.MPESA_BUSINESS_SHORTCODE,
            "PhoneNumber": phone_number,
            "CallBackURL": f"{settings.MPESA_CALLBACK_BASE_URL}/mpesa/callback/{booking_id}/",
            "AccountReference": f"Booking-{booking_id}",
            "TransactionDesc": f"Payment for Booking {booking_id}"
        }

        # Initiate STK Push
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        response = requests.post(
            'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest',
            json=payload,
            headers=headers,
            timeout=10
        )

        # Validate response
        if response.status_code == 200:
            payment_details = response.json()

            # Create payment record
            Payment.objects.create(

                booking=booking,
                user=request.user,
                amount=booking.total_price,
                payment_method='MPESA',
                status='PENDING',
                transaction_code=payment_details.get('CheckoutRequestID')
            )

            messages.success(request, "Payment request sent. Please complete payment on your phone.",extra_tags='payment')
            return render(request, 'payment_processing.html', {'booking': booking,'payment_response': payment_details})
        else:
            logger.error(f"STK Push failed: {response.text}")
            messages.error(request, "Payment initiation failed. Please try again.",extra_tags='payment')
            return redirect('my-bookings')

    except MPesaError as e:
        logger.error(f"MPesa Payment Error: {str(e)}")
        messages.error(request, f"Payment error: {str(e)}", extra_tags='payment')
        return redirect('my-bookings')
    except Exception as e:
        logger.error(f"Unexpected payment error: {str(e)}")
        messages.error(request, "An unexpected error occurred. Please try again.",extra_tags='payment')
        return redirect('my-bookings')


logger = logging.getLogger('mpesa')

@csrf_exempt
def mpesa_payment_callback(request, booking_id):
    """
    Handle MPesa payment callback
    """
    if request.method == 'POST':
        try:
            # Log raw callback data
            raw_data = request.body.decode('utf-8')
            logger.debug(f"Raw Callback Data: {raw_data}")

            # Parse callback data
            callback_data = json.loads(raw_data)
            logger.info(f"Parsed Callback Data: {callback_data}")

            # Extract relevant information
            stk_callback = callback_data.get('Body', {}).get('stkCallback', {})
            result_code = stk_callback.get('ResultCode')
            result_desc = stk_callback.get('ResultDesc', 'No description')
            checkout_request_id = stk_callback.get('CheckoutRequestID')

            # Retrieve booking and payment
            booking = get_object_or_404(Booking, id=booking_id)
            payment = get_object_or_404(Payment, booking=booking, transaction_code=checkout_request_id)

            # Process payment based on result code
            if result_code == 0:  # Successful payment
                payment.status = 'SUCCESS'
                payment.receipt_number = None  # Default value until extracted

                # Update booking status
                booking.status = 'PAID'

                # Extract additional transaction details
                metadata = stk_callback.get('CallbackMetadata', {}).get('Item', [])
                for item in metadata:
                    if item.get('Name') == 'MpesaReceiptNumber':
                        payment.receipt_number = item.get('Value')
                    elif item.get('Name') == 'Amount':
                        payment.amount = item.get('Value')
                    elif item.get('Name') == 'TransactionDate':
                        payment.transaction_date = item.get('Value')  # Parse if required
            else:
                payment.status = 'FAILED'
                payment.error_message = result_desc

                # Revert tour availability
                if hasattr(booking, 'tour'):
                    booking.tour.available_slots = max(0, booking.tour.available_slots + booking.slots_booked)
                    booking.tour.save()

            # Save changes
            payment.save()
            booking.save()

            logger.info(f"Payment status updated: {payment.status}, Booking ID: {booking.id}")

            return JsonResponse({
                "status": "success",
                "message": "Callback processed successfully"
            })

        except Booking.DoesNotExist:
            logger.error(f"Booking with ID {booking_id} does not exist.")
            return JsonResponse({"status": "error", "message": "Booking not found."}, status=404)

        except Payment.DoesNotExist:
            logger.error(f"Payment with transaction code {checkout_request_id} does not exist.")
            return JsonResponse({"status": "error", "message": "Payment record not found."}, status=404)

        except json.JSONDecodeError:
            logger.error("Failed to decode JSON from callback data.")
            return JsonResponse({"status": "error", "message": "Invalid JSON format."}, status=400)

        except Exception as e:
            logger.error(f"Callback processing error: {str(e)}")
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    return JsonResponse({"status": "error", "message": "Invalid request method."}, status=405)

@login_required
def cancel_booking(request, booking_id):
    if not request.user.is_authenticated:
        return redirect('login')
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if request.method == 'POST':
        booking.is_active = False
        booking.save()
        messages.success(request, "Booking cancelled successfully.")
        return redirect('my-bookings')

    context = {
        'booking': booking,
    }
    return render(request, 'cancel_booking.html', context)

def profile_management(request):
    return  render(request,'profile_manage.html')


def single_package(request, tour_id):
    tour = get_object_or_404(Tour, id=tour_id)
    context = {
        'tour': tour,
    }
    return render(request, 'single_package.html', context)
def reviews(request):
    return render(request,'reviews.html')

@login_required
def view_profile(request):
    if request.method == 'POST':
        user = request.user
        user.fullname = request.POST.get('fullname')
        user.email = request.POST.get('email')
        user.phone_number = request.POST.get('phone_number')

        # Handle profile picture upload
        if 'profile_picture' in request.FILES:
            user.profile_picture = request.FILES['profile_picture']

        user.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('my-profile')

    return render(request, 'profile_manage.html', {'user': request.user})




def payment_history(request):
    payments = Payment.objects.all()
    context ={'payments': payments}
    return render(request,'payment_history.html',context)