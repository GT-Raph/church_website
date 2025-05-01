from django.db import models
from django.utils.timezone import localdate
from urllib.parse import urlparse, parse_qs
import calendar

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to="events/", blank=True, null=True)
    
    # Standard event dates
    date = models.DateField()  # Start date
    end_date = models.DateField(blank=True, null=True)  # End date for multi-day events
    
    # Standard event times
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    
    # Recurring events
    is_recurring = models.BooleanField(default=False)  # Enable recurrence
    recurring_day = models.PositiveIntegerField(
        blank=True, null=True,
        help_text="Day of the month when this event repeats (e.g., 15 for the 15th)."
    )
    recurring_weekday = models.PositiveIntegerField(
        blank=True, null=True,
        choices=[(0, "Monday"), (1, "Tuesday"), (2, "Wednesday"), (3, "Thursday"),
                 (4, "Friday"), (5, "Saturday"), (6, "Sunday")],
        help_text="Choose if this event happens on a specific weekday (e.g., last Friday)."
    )
    recurring_week_position = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=[("first", "First"), ("second", "Second"), ("third", "Third"),
                 ("fourth", "Fourth"), ("last", "Last")],
        help_text="Select which occurrence of the weekday (e.g., 'Last' for last Friday)."
    )

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return self.title

    def get_next_occurrence(self):
        """Calculate the next occurrence of the event."""
        today = localdate()
        
        # Recurring event on a specific day of the month (e.g., every 15th)
        if self.is_recurring and self.recurring_day:
            next_date = today.replace(day=self.recurring_day)
            if next_date < today:  # If past, move to next month
                next_date = next_date.replace(month=today.month + 1, day=self.recurring_day)
            return next_date

        # Recurring event on a specific weekday position (e.g., last Friday)
        if self.is_recurring and self.recurring_weekday is not None and self.recurring_week_position:
            month = today.month
            year = today.year

            # Find all occurrences of that weekday in the month
            _, last_day = calendar.monthrange(year, month)
            weekdays = [
                day for day in range(1, last_day + 1)
                if calendar.weekday(year, month, day) == self.recurring_weekday
            ]

            if self.recurring_week_position == "last":
                return today.replace(day=weekdays[-1])
            elif self.recurring_week_position == "first":
                return today.replace(day=weekdays[0])
            elif self.recurring_week_position == "second":
                return today.replace(day=weekdays[1] if len(weekdays) > 1 else weekdays[0])
            elif self.recurring_week_position == "third":
                return today.replace(day=weekdays[2] if len(weekdays) > 2 else weekdays[0])
            elif self.recurring_week_position == "fourth":
                return today.replace(day=weekdays[3] if len(weekdays) > 3 else weekdays[0])

        return None  # No recurrence

class Sermon(models.Model):
    title = models.CharField(max_length=255)
    speaker = models.CharField(max_length=100)
    description = models.TextField()
    date = models.DateField()
    youtube_link = models.URLField(blank=True, null=True)
    audio_file = models.FileField(upload_to="sermons/", blank=True, null=True)

    def __str__(self):
        return f"{self.title} by {self.speaker}"

    def get_embed_url(self):
        """ Convert a standard YouTube link to an embeddable format """
        if self.youtube_link:
            parsed_url = urlparse(self.youtube_link)
            if "youtube.com" in parsed_url.netloc and "watch" in parsed_url.path:
                video_id = parse_qs(parsed_url.query).get("v")
                if video_id:
                    return f"https://www.youtube.com/embed/{video_id[0]}"
            elif "youtu.be" in parsed_url.netloc:
                return f"https://www.youtube.com/embed{parsed_url.path}"
        return self.youtube_link  # Return the original link if it's already correct

    def save(self, *args, **kwargs):
        """ Automatically convert YouTube links before saving """
        self.youtube_link = self.get_embed_url() if self.youtube_link else None
        super().save(*args, **kwargs)

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]  # Show latest messages first

    def __str__(self):
        return f"Message from {self.name}"


class Branch(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=255, blank=True, null=True)
    membership_code = models.CharField(max_length=10, blank=True, null=True)
   
    def save(self, *args, **kwargs):
        if not self.membership_code:
            # Use the first 2 uppercase letters of the branch name as the prefix
            code_prefix = self.name[:2].upper()

            # Count existing codes with the same prefix and increment the number
            existing_codes = Branch.objects.filter(membership_code__startswith=code_prefix).count()
            self.membership_code = f"{code_prefix}{existing_codes + 1:03}"  # Format: e.g., AP001, AP002

        super(Branch, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    def member_count(self):
        return self.members.count()


class Member(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    membership_code = models.CharField(max_length=20, blank=True, null=True)  # Optional
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name="members")
    registered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.branch.name}"
    



# class GalleryImage(models.Model):
#     title = models.CharField(max_length=255, blank=True, null=True)
#     image = models.ImageField(upload_to="gallery/")
#     uploaded_at = models.DateTimeField(auto_now_add=True)
#     position = models.PositiveIntegerField(default=0)  # Save order for display
    
    
#     class Meta:
#         ordering = ["position"]  # Sort by position

#     def __str__(self):
#         return self.title if self.title else "Gallery Image"