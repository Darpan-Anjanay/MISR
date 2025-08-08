from django.shortcuts import render
from django.shortcuts import render,redirect
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import AccessRequestForm
from .forms import AccessRequestForm
from .utlity import send_welcome_email  

# User Login 
def UserLogin(request):
    if request.method == "POST":
        username=request.POST['username']
        password=request.POST['password']
        user=authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            return redirect('dashboard')
        else:
            messages.info(request,'Invalid Creadentails')

    return  render(request,"Auth/UserLogin.html")


# Logout
@login_required(login_url='login')
def UserLogout(requset):
     logout(requset)
     return redirect('login')







# Request Access 
def RequestAccess(request):
    if request.method == 'POST':
        form = AccessRequestForm(request.POST)
        if form.is_valid():
            access = form.save()

           
            subject = "Multi-Shop Inventory Access Request Received"
            message = f"""
Dear {access.full_name},

Thank you for requesting access to the Multi-Shop Inventory & Sales Reporting System.

* Real-time tracking, Google Sheet integration, and shop-wise dashboards — all in one place.
* Shop Management: Shop-wise Control with personalized access.
* Google Sheets Integration: Sync purchase/sales data directly.
* Dashboard Reports: View inventory summaries, profits, and trends.

Our team will contact you shortly.

Best regards,  
Team Multi-Shop Inventory  
Built with Django & Google Sheets API
            """
            from_email = "darpangurjarcodeai28@gmail.com"
            recipient_list = [access.email]

            send_welcome_email(subject, message, from_email, recipient_list)

            return render(request, 'Auth/landing.html')
    else:
        form = AccessRequestForm()
    return render(request, 'Auth/RequestAccess.html', {'form': form})
