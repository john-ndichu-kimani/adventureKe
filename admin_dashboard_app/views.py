from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect, get_object_or_404
from adventureApp.models import TourGuide, User, Tour, Destination, Booking


# Create your views here.

@login_required(login_url='login')
def dashboard(request):
    tours_count = Tour.objects.all().count()
    users_count = User.objects.all().count()
    guides_count = TourGuide.objects.all().count()
    bookings_count = Booking.objects.all().count()
    context = {'tours_count': tours_count, 'users_count': users_count, 'guides_count': guides_count,'bookings_count': bookings_count}
    return render(request,'dashboard.html')

@login_required(login_url='login')
def user_profile(request):
    user = request.user
    context = {'user': user}
    return render(request,'profile.html',context)


@login_required(login_url='login')

def update_profile(request):
    if request.method == 'POST':
        user = request.user

        # Get form data
        fullname = request.POST.get('fullname')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        profile_picture = request.FILES.get('profile_picture')

        try:
            # Update user information
            user.fullname = fullname
            user.email = email
            user.phone_number = phone_number


            # Update profile picture if provided
            if profile_picture:
                user.profile_picture = profile_picture

            # Save the updated user
            user.save()

            # Add a success message
            messages.success(request, 'Profile updated successfully.',extra_tags='update_profile')

            # Redirect to the dashboard or a specific URL

            return redirect('/admin-dashboard/profile/')

        except ValidationError as e:
            # Handle validation errors
            messages.error(request, str(e))
        except Exception as e:
            # Handle any other unexpected errors
            messages.error(request, 'An error occurred while updating your profile.',extra_tags='update_profile')

    # If not a POST request, redirect to dashboard
    return redirect('dashboard')


@login_required(login_url='login')
def ban_user(request, user_id):
    """
    View to ban or unban a user
    Requires admin or staff permissions
    """
    # Check if the current user has permission to ban users
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, 'You do not have permission to ban users.')
        return redirect('clients-manage')

    try:
        # Get the user to be banned
        user = User.objects.get(id=user_id)

        # Toggle user's active status
        if user.is_active:
            user.is_active = False
            messages.success(request, f'User {user.fullname} has been banned.')
        else:
            user.is_active = True
            messages.success(request, f'User {user.fullname} has been unbanned.')

        user.save()
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')

    return redirect('clients-manage')


# Update the clients_manage view to show ban status
@login_required(login_url='login')
def clients_manage(request):
    # Check if the current user has permission to manage clients
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, 'You do not have permission to manage clients.')
        return redirect('dashboard')

    users = User.objects.filter(is_staff=False, is_superuser=False)
    context = {'clients': users}
    return render(request, 'clients_manage.html', context)


def guides_manage(request):
    guides = TourGuide.objects.all()
    context = {'guides':guides}
    return render(request,'guides_manage.html',context)

@login_required(login_url='login')
def user_bookings(request):
    bookings = Booking.objects.all()
    context = {'bookings':bookings}
    return render(request,'bookings.html',context)

@login_required(login_url='login')
def reviews(request):
    user_reviews = User.objects.all()
    context = {'reviews':user_reviews}
    return render(request,'reviews.html',context)

@login_required
def create_or_update_tour(request, tour_id=None):
    # If tour_id is provided, we're updating an existing tour
    if tour_id:
        tour = get_object_or_404(Tour, id=tour_id)
        page_title = 'Update Tour Package'
    else:
        tour = None
        page_title = 'Create Tour Package'

    if request.method == 'POST':
        # Get data from form
        title = request.POST.get('title')
        description = request.POST.get('description')
        price = request.POST.get('price')
        destination_id = request.POST.get('destinations')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        max_group_size = request.POST.get('max_group_size')
        min_group_size = request.POST.get('min_group_size')
        slots = request.POST.get('slots')
        featured_image = request.FILES.get('featured_image')

        # Get the destination object
        destination = Destination.objects.get(id=destination_id)

        # Create or update the tour package
        if tour:
            # Update existing tour
            tour.title = title
            tour.description = description
            tour.price = price
            tour.destination = destination
            tour.start_date = start_date
            tour.end_date = end_date
            tour.max_group_size = max_group_size
            tour.min_group_size = min_group_size
            tour.available_slots = slots

            # Only update image if a new one is provided
            if featured_image:
                tour.featured_image = featured_image

            tour.save()
            messages.success(request, 'Tour updated successfully.')
        else:
            # Create new tour
            Tour.objects.create(
                title=title,
                description=description,
                price=price,
                destination=destination,
                start_date=start_date,
                end_date=end_date,
                max_group_size=max_group_size,
                min_group_size=min_group_size,
                available_slots=slots,
                featured_image=featured_image
            )
            messages.success(request, 'Tour created successfully.')

        return redirect('tours-manage')

    # For GET request, render the form
    destinations = Destination.objects.all()
    context = {
        'destinations': destinations,
        'tour': tour,
        'page_title': page_title
    }
    return render(request, 'create_tour.html', context)

@login_required
def delete_tour(request, tour_id):
    tour = Tour.objects.get(id=tour_id)
    if request.method == 'POST':
        tour.delete()
        messages.success(request, 'Tour deleted successfully.')
        return redirect('tours-manage')

    # Render a confirmation page
    return render(request, 'delete_confirm.html', {'tour': tour})

@login_required(login_url='login')
def tours_manage(request):
    tours = Tour.objects.all()
    context = {'tours':tours}
    return render(request,'tours_manage.html',context)



@login_required(login_url='login')
def view_tour(request, pk):
    tour = Tour.objects.get(pk=pk)
    context = {'tour': tour}
    return render(request,'single-tour')


@login_required(login_url='login')
def analytics(request):
    return render(request,'analytics.html')

@login_required(login_url='login')
def logout(request):
    return render(request,'logout.html')



