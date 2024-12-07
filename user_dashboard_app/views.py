from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect

from adventureApp.models import Tour,Booking
from adventureApp.forms import BookingForm, TourSearchForm


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
                Q(destination__icontains=query) |
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
def book_tour(request, tour_id):
    if not request.user.is_authenticated:
        return redirect('login')
    tour = get_object_or_404(Tour, id=tour_id)

    if tour.available_slots <= 0:
        messages.error(request, "This tour is fully booked.")
        return redirect('user-dashboard')

    if request.method == 'POST':
        form = BookingForm(request.POST, tour=tour, user=request.user)
        if form.is_valid():
            try:
                booking = form.save()
                messages.success(
                    request,
                    f"Successfully booked {booking.slots_booked} slot(s) for {tour.title}"
                )
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
    if not request.user.is_authenticated:
        return redirect('login')
    bookings = Booking.objects.filter(user=request.user, is_active=True)
    context = {
        'bookings': bookings,
    }
    return render(request, 'my_bookings.html', context)


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
def payment_history(request):
    return render(request,'payment_history.html')