from django.contrib import admin, messages

from .emails import EmailError, render_newsletter_html, send_email
from .models import Article, Category, ContactMessage, Newsletter, Subscriber, Video

admin.site.register(Article)
admin.site.register(Category)
admin.site.register(Video)


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'name', 'email', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('email',)


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('subject', 'created_at', 'sent_at', 'sent_count')
    readonly_fields = ('sent_at', 'sent_count')
    actions = ['send_test']

    @admin.action(description="Envoyer un test à mon adresse email")
    def send_test(self, request, queryset):
        if not request.user.email:
            self.message_user(request, "Ton compte administrateur n'a pas d'adresse email.", messages.ERROR)
            return
        for newsletter in queryset:
            try:
                send_email(
                    request.user.email,
                    f"[TEST] {newsletter.subject}",
                    render_newsletter_html(newsletter),
                )
            except EmailError as exc:
                self.message_user(request, str(exc), messages.ERROR)
                return
        self.message_user(request, f"Test envoyé à {request.user.email}.", messages.SUCCESS)