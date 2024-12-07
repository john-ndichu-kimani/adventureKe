from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from adventureApp.models import TourGuide, User, Tour, Destination


# Create your views here.

@login_required(login_url='login')
def dashboard(request):
    return render(request,'dashboard.html')

@login_required(login_url='login')
def user_profile(request):
    user = request.user
    context = {'user': user}
    return render(request,'profile.html',context)

@login_required(login_url='login')
def clients_manage(request):
    users = User.objects.all()
    context = {'clients': users}
    return render(request,'clients_manage.html',context)


def guides_manage(request):
    guides = TourGuide.objects.all()
    context = {'guides':guides}
    return render(request,'guides_manage.html',context)

@login_required(login_url='login')
def user_bookings(request):
    bookings = TourGuide.objects.all()
    context = {'bookings':bookings}
    return render(request,'bookings.html',context)

@login_required(login_url='login')
def reviews(request):
    user_reviews = User.objects.all()
    context = {'reviews':user_reviews}
    return render(request,'reviews.html',context)

def create_tour(request):
    """
    View function to create a new tour
    """
    if request.method == 'POST':
        try:
            # Get form data from POST request
            title = request.POST.get('title')
            description = request.POST.get('description')
            price = request.POST.get('price')
            destination_id = request.POST.get('destinations')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            max_group_size = request.POST.get('max_group_size')
            min_group_size = request.POST.get('min_group_size')
            available_slots = request.POST.get('slots')
            featured_image = request.FILES.get('featured_image')

            # Validate required fields
            if not all([title, description, price, destination_id, start_date, end_date]):
                messages.error(request, "Please fill in all required fields.")
                return redirect('tours-manage')

            # Get destination
            try:
                destination = Destination.objects.get(id=destination_id)
            except Destination.DoesNotExist:
                messages.error(request, "Invalid destination selected.")
                return redirect('tours-manage')

            # Create tour instance
            tour = Tour(
                title=title,
                description=description,
                price=price,
                destination=destination,
                start_date=start_date,
                end_date=end_date,
                max_group_size=max_group_size or 1,
                min_group_size=min_group_size or 1,
                available_slots=available_slots or 0,
                featured_image=featured_image
            )

            # Full clean to run model validators
            try:
                tour.full_clean()
            except ValidationError as e:
                # Collect and display validation errors
                for field, errors in e.message_dict.items():
                    messages.error(request, f"{field.capitalize()}: {', '.join(errors)}")
                return redirect('tours-manage')

            # Save the tour
            tour.save()

            # Success message
            messages.success(request, f"Tour '{tour.title}' created successfully!")
            return redirect('tours-manage')

        except Exception as e:
            # Catch any unexpected errors
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('tours-manage')

    # Handle GET request - render the page with destinations
    destinations = Destination.objects.all()
    print(Destination.objects.all())
    return render(request, 'create_tour.html', {'destinations': destinations})

@login_required(login_url='login')
def tours_manage(request):
    tours = Tour.objects.all()
    context = {'tours':tours}
    return render(request,'tours_manage.html',context)


@login_required(login_url='login')
def delete_tour(request, pk):
    tour = Tour.objects.get(pk=pk)
    tour.delete()
    return redirect('tours-manage')

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



