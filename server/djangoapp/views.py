from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import CarDealer, DealerReview, CarModel, CarMake
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
# def about(request):
def about(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/about.html', context)


# Create a `contact` view to return a static contact page
#def contact(request):
def contact(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/contact.html', context)

# Create a `login_request` view to handle sign in request
# def login_request(request):
def login_request(request):
    context = {}
    # Handles POST request
    if request.method == "POST":
        # Get username and password from request.POST dictionary
        username = request.POST['username']
        password = request.POST['psw']
        # Try to check if provide credential can be authenticated
        user = authenticate(username=username, password=password)
        if user is not None:
            # If user is valid, call login method to login current user
            login(request, user)
    return redirect('djangoapp:index')
    """    else:
            # If not, return to login page again
            return render(request, 'djangoapp/user_login.html', context)
    else:
        return render(request, 'onlinecourse/user_login.html', context)"""

# Create a `logout_request` view to handle sign out request
# def logout_request(request):
def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
# def registration_request(request):
def registration_request(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/registration.html', context)
    # If it is a POST request
    elif request.method == 'POST':
        # Get user information from request.POST
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            # Check if user already exists
            User.objects.get(username=username)
            user_exist = True
        except:
            # If not, simply log this is a new user
            logger.debug("{} is new user".format(username))
        # If it is a new user
        if not user_exist:
            # Create user in auth_user table
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            # Login the user and redirect to course list page
            login(request, user)
            return redirect("djangoapp:index")
        else:
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    if request.method == "GET":
        context = {}
        #url = "https://us-south.functions.cloud.ibm.com/api/v1/namespaces/59133c61-5d7c-493b-a86f-a7fe68b99f3e/actions/dealership-package/get-dealership"
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/59133c61-5d7c-493b-a86f-a7fe68b99f3e/dealership-package/get-dealership"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        context["dealership_list"] = dealerships
        # Concat all dealer's short name
        #dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short name
        #return HttpResponse(dealer_names)
        print("context")
        print(context)
        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
def get_dealer_details(request, dealer_id):
    context = {}
    url = "https://us-south.functions.cloud.ibm.com/api/v1/namespaces/59133c61-5d7c-493b-a86f-a7fe68b99f3e/actions/review-package/get-review"
    url = "https://us-south.functions.appdomain.cloud/api/v1/web/59133c61-5d7c-493b-a86f-a7fe68b99f3e/review-package/get-review"
    kwargs = {"dealerid": dealer_id}
    dealer_details = get_dealer_reviews_from_cf(url, dealerid=dealer_id)
    # Get dealers from the URL
    #dealer_details = get_dealer_reviews_from_cf(url,dealer_id)
    context["dealer_id"]=dealer_id
    context["reviews"]=dealer_details
    return render(request, 'djangoapp/dealer_details.html', context)

# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):
def add_review(request, dealer_id):
    context = {}
    if request.method == "GET":
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/59133c61-5d7c-493b-a86f-a7fe68b99f3e/dealership-package/get-dealership"
        """dealer = get_dealer_details(url, dealer_id=dealer_id)
        cars = CarModel.objects.filter(dealer_id=dealer_id)
        context["cars"] = cars
        context["dealer"] = dealer
        return render(request, 'djangoapp/add_review.html', context)"""
        dealers = get_dealers_from_cf(url, dealerid=dealer_id)
        for dealer in dealers:
            if dealer.id == dealer_id:
                dealer_name = dealer.full_name
        context = {
            "dealer_id": dealer_id,
            "dealer_name": dealer_name,
            "cars": CarModel.objects.filter(dealer_id=dealer_id)
        }
        #print(context)
        return render(request, 'djangoapp/add_review.html', context)

    if request.method == "POST":
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/59133c61-5d7c-493b-a86f-a7fe68b99f3e/review-package/get-review"      
        if 'purchasecheck' in request.POST:
            was_purchased = True
        else:
            was_purchased = False
        cars = CarModel.objects.filter(dealer_id=dealer_id)
        for review_car in cars:
            if review_car.id == int(request.POST['car']):
                car = review_car  
        review = {}
        review["time"] = datetime.utcnow().isoformat()
        review["name"] = request.POST['name']
        review["dealership"] = dealer_id
        review["review"] = request.POST['content']
        review["purchase"] = was_purchased
        review["purchase_date"] = request.POST['purchasedate']
        review["car_make"] = car.make.name
        review["car_model"] = car.name
        review["car_year"] = car.year.strftime("%Y")
        json_payload = {}
        json_payload["review"] = review
        response = post_request(url, json_payload)
        return redirect("djangoapp:dealer_details", dealer_id=dealer_id)
