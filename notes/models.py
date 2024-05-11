from django.db import models
from django.urls import reverse
from django.utils import safestring, timezone
from markdown_it import MarkdownIt

from notes.utils import generate_reference_code


class Note(models.Model):
    code = models.CharField(
        max_length=9, editable=False, unique=True, default=generate_reference_code
    )
    text = models.TextField()
    promoted = models.BooleanField(default=False)
    last_drilled = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)

    @property
    def html(self):
        return safestring.mark_safe(MarkdownIt().render(self.text))

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return str(self.code)

    def get_absolute_url(self):
        return reverse("notes:detail-note", kwargs={"slug": self.code})
