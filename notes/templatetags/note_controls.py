from django import template
from django.urls import reverse

register = template.Library()


@register.inclusion_tag("notes/templatetags/note_controls.html")
def note_controls(note, request):
    controls = []

    # Delete note
    controls.append(
        {
            "method": "get",
            "action": reverse(
                "notes:delete-note",
                kwargs={"slug": note.code},
            ),
            "icon": "trash",
            "text": "Delete",
        }
    )

    return {
        "controls": controls,
        "request": request,
    }
