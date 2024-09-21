from django.shortcuts import render,redirect
import requests
from django.contrib import messages
from .forms import CountryForm,SortForm,LanguageForm,QueryForm
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout,get_user_model
from django.contrib.auth.forms import PasswordResetForm
from .forms import RegistrationForm,LoginForm
from .models import Subscription_Model
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.db.models.query_utils import Q
from django.contrib.auth.tokens import default_token_generator
import razorpay
from django.views.decorators.csrf import csrf_exempt
from .tasks import sending_mails
from django.utils import timezone

# Create your views here.
def index(request):
    if request.method == 'POST':
        query = QueryForm(request.POST)
        if query.is_valid():
            email = query.cleaned_data.get('email')
            name = query.cleaned_data.get('name')
            subject = query.cleaned_data.get('subject')
            content = query.cleaned_data.get('query')
            send_subject = f"{subject} from {name}"
            send_message = f"Recived From:\nEmail: {email}\nName: {name}\nMessage:\n{content}"
            result = sending_mails.delay(send_subject,send_message,'newsreader018@gmail.com',['newsreader018@gmail.com'])
            if result:
                messages.success(request,"Query Sent Successfully!!!")
            else:
                messages.error(request,"Could'nt Sent the Query, Please Try again!!!")
            query = QueryForm()
            return redirect('home')
    else:
        query = QueryForm()
    return render(request,'home.html',{'form':query})

@login_required(login_url='/login/')
def news(request):
    try:
        user = request.user
        country_form = CountryForm(request.POST or None)
        sort_form = SortForm(request.POST or None)
        language_form = LanguageForm(request.POST or None)

        selected_language = request.POST.get("language") or "en"
        selected_sort = request.POST.get('sort') or "published_desc"
        selected_country = request.POST.get('countries') or "in"
        category = request.GET.get('category','general')
        keyword = request.GET.get('keyword','general')

        if request.method == "POST" and country_form.is_valid():
            selected_country = country_form.cleaned_data['country']

        API_KEY = settings.NEWS_API_KEY
        url = f"http://api.mediastack.com/v1/news?access_key={API_KEY}&keywords={keyword}&countries={selected_country}&sort={selected_sort}&languages={selected_language}&categories={category}"

        response = requests.get(url)
        json_response = response.json().get('data',[])
        articles = []
        titles = set()
        for article in json_response:
            title = article.get('title')
            if title not in titles:
                titles.add(title)
                articles.append(article)
        total = len(articles)
        try:
            premium = Subscription_Model.objects.get(user=user)
            subscribed = premium.subscription
        except Subscription_Model.DoesNotExist:
            subscribed = False
        

        return render(request,'news.html',{'articles':articles if subscribed else articles[:3], 'form':country_form, 'total_response':total, 'sort_form':sort_form, 'language_form':language_form})
    
    except Exception as error:
        return render(request,'error_page.html',{'error':error})
    

def Login(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request,user)
            Subscription_Model.objects.get_or_create(user = user)
            return redirect('home')
        else:
            messages.error(request,"Invalid Credentials!")
    else:
        form = LoginForm()
    return render(request,'login.html',{'form':form})

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active=False
            user.save()
            activateEmail(request, user, form.cleaned_data.get('email'))
            return redirect('home')
        else:
            messages.error(request,"Invalid Credentials!")
    else:
        form = RegistrationForm()
    return render(request,'register.html',{'form':form})

def logout(request):
    auth_logout(request)
    return redirect('home')

@login_required(login_url='/login/')
def premium(request):
    client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET_KEY))
    if request.method == 'POST':
        if Subscription_Model.objects.filter(user=request.user).exists():
            messages.error(request,"You are Already a Premium User, Kindly wait for your Membership to expire then you can Subscribe again")
            return redirect('home')
        subscription_type = request.POST.get('subscription_type')
        if subscription_type == "monthly":
            amount = 100
        elif subscription_type == "yearly":
            amount = 200
        else:
            messages.error(request,"Invalid Subscription Type!")
        currency = "INR"
        order_data = {
            'amount':amount,
            'currency':currency,
            'payment_capture':'1'
        }
        order = client.order.create(data=order_data)
        context = {
            'order_id': order['id'],
            'amount':amount,
            'subscription_type':subscription_type,
            'razorpay_key_id': settings.RAZORPAY_API_KEY
        }
        return render(request,'payment.html',context)

    return render(request,'premium.html')

@csrf_exempt
def payment_success(request,subscription_type):
    # Handle successful payment
    premium,created = Subscription_Model.objects.get_or_create(user=request.user)
    premium.subscription_type = subscription_type
    premium.subscription_start = timezone.now()
    premium.subscription = True
    premium.save()
    subject = "Many Many Congradulations🎉🎉🎉 for Becoming a Premium user"
    message = render_to_string('premium_thanks.html',{'user':premium.user,'type':subscription_type})
    email = premium.user.email
    sending_mails(subject,message,'',[email])
    return render(request, 'home.html')

@csrf_exempt
def payment_failure(request):
    # Handle failed payment
    return render(request, 'payment_failure.html')

def activate(request, uidb64,token):
    User_Model = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User_Model.objects.get(pk=uid)
    except Exception as error:
        user = None
        return render(request,'error_page.html',{'error':error})
    if user is not None:
        user.is_active=True
        user.save()
        auth_login(request,user)
        Subscription_Model.objects.get_or_create(user = user)
        messages.success(request,"Thank You for Your Activation! Have fun reading news!!!")
        subject = f"Thanks for Registering to News Reader, we Welcome you {user} with warm regards"
        message_template = 'activation_thanks.html'
        params = {'user':user}
        message = render_to_string(message_template,params)
        email = user.email
        sending_mails(subject,message,'',[email]) 
    else:
        user.delete()
        messages.error(request,"Invalid Link")
    return redirect('home')

def activateEmail(request,user,to_email):
    email_subject = "Activate Your User Account"
    email_template_name = "activate_account.html"
    parameters = {
                'user':user,
                'domain': get_current_site(request).domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token':default_token_generator.make_token(user),
                'protocol': 'https' if request.is_secure() else 'http'
    }
    email_message = render_to_string(email_template_name,parameters)
    result = sending_mails(email_subject, email_message,'',[to_email])
    if result:
        messages.success(request,f"Dear {user}, please go to your email {to_email} inbox and click on recived activation link to confirm and complete the registration process. Note: Check your spam Folder too is you don't fint any mail.")
    else:
        messages.error(request,f"Problem Sending email to {to_email}, Check if you typed it correctly.")

def password_reset_request(request):
    if request.method == 'POST':
        password_form = PasswordResetForm(request.POST)
        if password_form.is_valid():
            data = password_form.cleaned_data.get('email')
            user_email = User.objects.filter(Q(email=data))
            if user_email.exists():
                for user in user_email:
                    subject = "Password Reset Request"
                    email_template_name = 'password_mail.html'
                    parameters = {
                        'user': user,
                        'email':user.email,
                        'domain': get_current_site(request).domain,
                        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                        'token':default_token_generator.make_token(user),
                        'protocol': 'https' if request.is_secure() else 'http'
                    }
                    email = render_to_string(email_template_name, parameters)
                    result = sending_mails(subject,email,'',[user.email])
                    if not result:
                        return HttpResponse("Invalid Header!!!")
                    
                    return redirect('password_reset_done')
    else:
        password_form = PasswordResetForm()
    return render(request, 'password_reset.html',{'form':password_form})

@login_required
def cancel_subscription(request):
    if request.method == "POST":
        try:
            user = Subscription_Model.objects.get(user=request.user)
            user.delete()
            messages.success(request,"Successfully cancelled your Subscription!")
            subject = f"Sorry {user.user} That you have to cancel Your Premium Membership"
            message = render_to_string('cancel_premium.html',{'user':user.user})
            email = user.user.email
            sending_mails(subject,message,'',[email])
            return redirect('home')
        except:
            messages.error(request,"Something Wrong Happened! Please restart the site and try Again!!!")
            return redirect('home')
    return render(request,'cancel_subscription.html')
