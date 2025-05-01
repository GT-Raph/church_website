from django.shortcuts import render, redirect
from django.utils.timezone import localdate
from django.contrib import messages 
from .models import Event, Sermon, ContactMessage # HeroImage
from django.core.mail import send_mail
from .forms import ContactForm, MemberRegistrationForm
from datetime import date
import calendar
import random

def home(request):
    # hero_image = HeroImage.objects.all()
    events = Event.objects.all()
    sermons = Sermon.objects.all()
    today = date.today()
    
    upcoming_events = Event.objects.filter(date__gte=today).order_by('date')[:5]  # Limit to 5 upcoming events
    past_events = Event.objects.filter(date__lt=today).order_by('-date')[:5]  # Limit to 5 past events
    return render(request, 'main/home.html', {
        # 'hero_image': hero_image,
        'events': events, 
        'sermon': Sermon,
        "upcoming_events": upcoming_events,
        "past_events": past_events if past_events.exists() else None,
    })

def contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        # Save the message to the database
        ContactMessage.objects.create(name=name, email=email, message=message)

        messages.success(request, "Your message has been sent successfully!")  # This was causing the error

        return redirect("contact")  # Redirect to avoid form resubmission

    return render(request, "main/contact.html")

def event(request):
    today = localdate()
    current_month = today.month
    current_year = today.year

    # Get non-recurring future events
    upcoming_events = list(Event.objects.filter(
        end_date__gte=today
    ) | Event.objects.filter(
        date__gte=today, end_date__isnull=True, is_recurring=False
    ))

    # Get recurring events that occur in the current month
    recurring_events = Event.objects.filter(is_recurring=True)
    recurring_filtered = {}

    for event in recurring_events:
        next_date = event.get_next_occurrence()
        if next_date and next_date.year == current_year and next_date.month == current_month:
            if event.title not in recurring_filtered:
                event.next_occurrence = next_date
                recurring_filtered[event.title] = event

    # Merge one-time and filtered recurring events
    upcoming_events += list(recurring_filtered.values())

    # Get past events (excluding recurring ones)
    past_events = Event.objects.filter(
        end_date__lt=today
    ) | Event.objects.filter(
        date__lt=today, end_date__isnull=True, is_recurring=False
    )

    return render(request, "main/event.html", {
        "upcoming_events": upcoming_events,
        "past_events": past_events if past_events.exists() else None,
        "today": today,  # Pass 'today' to the template
    })
    
def sermons(request):
    sermons = Sermon.objects.order_by("-date")  # Latest sermons first
    return render(request, "main/sermons.html", {"sermons": sermons})

def giving(request):
    return render(request, "main/giving.html")

def register_member(request):
    if request.method == "POST":
        form = MemberRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('register_member')  # Redirect after successful registration
    else:
        form = MemberRegistrationForm()

    return render(request, "main/register.html", {"form": form})