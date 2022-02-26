from django.shortcuts import render, redirect
from django.http import HttpResponse
from SaurabhComputerApp.models import Product,Contact,Orders,OrderUpdate,Blogpost,Services
from math import ceil
from django.views.decorators.csrf import csrf_exempt
from Paytm import Checksum
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
import json
MERCHANT_KEY = '8ncW%Jj%nY8Pb67@'


# Create your views here.
def index(request):
    products = Product.objects.all()
    # n = len(products)
    # numslids = n//4 + ceil((n/4)-(n//4))
    allProds=[]
    catprods= Product.objects.values('category', 'id')
    cats= {item["category"] for item in catprods}
    for cat in cats:
        prod=Product.objects.filter(category=cat)
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod, range(1, nSlides), nSlides])
    #params={'no_of_slides':numslids, 'range':range(1,numslids), 'product': products}
    # allProds=[[products, range(1, len(products)), numslids],[products, range(1, len(products)), numslids]]
    params={'allProds':allProds }
    return render(request,'index.html', params)
    
def home(request):
    return redirect('/')

def about(request):
    if request.user.is_anonymous:
        messages.error(request,"Please Login the site!")
        return redirect('/')
    return render(request,'about.html')

def contact(request):
    thank = False
    if request.method=="POST":
        name=request.POST.get('name', '')
        email=request.POST.get('email', '')
        phone=request.POST.get('phone', '')
        desc=request.POST.get('desc', '')
        contact = Contact(name=name, email=email, phone=phone, desc=desc)
        contact.save()
        thank = True
    if request.user.is_anonymous:
        messages.error(request,"Please Login the site!")
        return redirect('/')
    return render(request,'contact.html', {'thank': thank})


def tracker(request):
    if request.method=="POST":
        orderId = request.POST.get('orderId', '')
        email = request.POST.get('email', '')
        try:
            order = Orders.objects.filter(order_id=orderId, email=email)
            if len(order)>0:
                update = OrderUpdate.objects.filter(order_id=orderId)
                updates = []
                for item in update:
                    updates.append({'text': item.update_desc, 'time': item.timestamp})
                    response = json.dumps({"status":"success", "updates": updates, "itemsJson": order[0].items_json}, default=str)
                return HttpResponse(response)
            else:
                return HttpResponse('{"status":"noitem"}')
        except Exception as e:
            return HttpResponse('{"status":"error"}')
    return render(request,'tracker.html')



def searchMatch(query, item):
    '''return true only if query matches the item'''
    if query in item.desc.lower() or query in item.product_name.lower() or query in item.category.lower():
        return True
    else:
        return False


def search(request):
    query = request.GET.get('search')
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prodtemp = Product.objects.filter(category=cat)
        prod = [item for item in prodtemp if searchMatch(query, item)]

        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        if len(prod) != 0:
            allProds.append([prod, range(1, nSlides), nSlides])
    params = {'allProds': allProds, "msg": ""}
    if len(allProds) == 0 or len(query)<4:
        params = {'msg': "Please make sure to enter relevant search query"}
    return render(request, 'search.html', params)

def prodView(request, myid):
    #fetch the product using id
    product = Product.objects.filter(id=myid)
    return render(request,'productview.html',{'product':product[0]})

def checkout(request):
    if request.user.is_anonymous:
        messages.error(request,"Please Login the site!")
        return redirect('/')
    if request.method=="POST":
        items_json=request.POST.get('itemsJson', '')
        name=request.POST.get('name', '')
        amount=request.POST.get('amount', '')
        email=request.POST.get('email', '')
        address=request.POST.get('address1', '') + " " + request.POST.get('address2', '')
        city=request.POST.get('city', '')
        state=request.POST.get('state', '')
        zip_code=request.POST.get('zip_code', '')
        phone=request.POST.get('phone', '')

        order = Orders(items_json=items_json, name=name, email=email, address= address, city=city, state=state, zip_code=zip_code, phone=phone, amount=amount)
        order.save()
        update = OrderUpdate(order_id=order.order_id, update_desc="Your order has been placed")
        update.save()
        thank = True
        id = order.order_id
        #return render(request,'checkout.html', {'thank':thank, 'id': id})
        # Request paytm to transfer the amount to your account after payment by user
        param_dict = {
                'MID': 'PfveGw95844610988640',
                'ORDER_ID': str(order.order_id),
                'TXN_AMOUNT': str(amount),
                'CUST_ID': email,
                'INDUSTRY_TYPE_ID': 'Retail',
                'WEBSITE': 'WEBSTAGING',
                'CHANNEL_ID': 'WEB',
                'CALLBACK_URL':'http://127.0.0.1:8000/handlerequest',

        }
        param_dict['CHECKSUMHASH'] = Checksum.generate_checksum(param_dict, MERCHANT_KEY)
        return render(request, 'paytm.html', {'param_dict': param_dict})
    return render(request,'checkout.html')


@csrf_exempt
def handlerequest(request):
    # paytm will send you post request here
    form = request.POST
    response_dict = {}
    #checksum = ""
    for i in form.keys():
        response_dict[i] = form[i]
        if i == 'CHECKSUMHASH':
            checksum = form[i]
            
    verify = Checksum.verify_checksum(response_dict, MERCHANT_KEY, checksum)
    if verify:
        if response_dict['RESPCODE'] == '01':
            print('order successful')
        else:
            print('order was not successful because' + response_dict['RESPMSG'])
    return render(request, 'Paymentstatus.html', {'response': response_dict})

def blog(request): #id variable access
    post = Blogpost.objects.all()
    if request.user.is_anonymous:
        messages.error(request,"Please Login the site!")
        return redirect('/')
    return render(request,'blog.html', {'post':post})

def blogpost(request, id):
    mypost = Blogpost.objects.filter(post_id = id)[0]
    return render(request,'blogpost.html', {'mypost':mypost})

def register(request):
    if request.method == 'POST':
        # Get the post member
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        #check for errorneous user
        if len(username) > 10:
            messages.success(request, "Username must be under 10 character")
            return redirect('/')

        if not username.isalnum():
            messages.success(request, "Username should only contain letters and numbers")
            return redirect('/')

        if password1 != password2:
            messages.success(request, "Passwords do not match")
            return redirect('/')

        # create the user
        myuser = User.objects.create_user(username, email, password1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.save()
        messages.success(request, "Your icoder account has been successfully createed")
        return redirect('/')
    else:
        return HttpResponse('Error 404 User not allow')

def loginUser(request):
    if request.method == 'POST':
        # Get the post member
        loginuser = request.POST['loginuser']
        password = request.POST['password']

        user = authenticate(username=loginuser, password=password)
        if user is not None:
            login(request, user)
            messages.success(request,"Successfully Logged In")
            return redirect('/')
        else:
            messages.error(request,"Invalid Credentials, please try again")
            return redirect('/')
    return HttpResponse('Error 404 User not allow')
def logoutUser(request):
    logout(request)
    messages.success(request,"Successfully Logged Out")
    return redirect('/')

def services(request):
    post = Services.objects.all()
    if request.user.is_anonymous:
        messages.error(request,"Please Login the site!")
        return redirect('/')
    return render(request,'services.html', {'post':post})
