import itertools
import random

from django.contrib.auth import get_user_model
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.core.paginator import EmptyPage, Paginator
from django.forms import modelform_factory
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic import DeleteView, DetailView, ListView
from formtools.preview import FormPreview

from .models import Note


UserModel = get_user_model()

NoteForm = modelform_factory(Note, fields=["text"])


class GracefulPaginator(Paginator):
    """
    django.core.paginator.Paginator modified so that page() behaves
    like get_page() when receiving a page number greater than num_pages.
    Solution from https://stackoverflow.com/a/40835335/14354604.
    """

    def validate_number(self, number):
        try:
            return super().validate_number(number)
        except EmptyPage:
            if number > 1:
                return self.num_pages
            raise


class GracefulListView(ListView):
    paginator_class = GracefulPaginator


class _CreateNote(FormPreview):
    form_template = "notes/note_form.html"
    preview_template = "notes/note_form_preview.html"

    def done(self, request, cleaned_data):
        note = Note.objects.create(**cleaned_data)
        return HttpResponseRedirect(note.get_absolute_url())


create_note = _CreateNote(NoteForm)
"""View function for creating a Note with a preview stage."""


class ListNotes(GracefulListView):
    model = Note
    paginate_by = 10


class ListPromotedNotes(ListNotes):
    def get_queryset(self):
        return Note.objects.filter(promoted=True)


class SearchNotes(ListNotes):
    def get_queryset(self):
        qs = super().get_queryset()
        vector = SearchVector("text")
        query = SearchQuery(self.request.GET.get("query", ""))
        return (
            qs.annotate(search=vector, rank=SearchRank(vector, query))
            .filter(search=query)
            .order_by("-rank")
        )


class DetailNote(DetailView):
    model = Note
    slug_field = "code"


class DeleteNote(DeleteView):
    model = Note
    slug_field = "code"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "redirect_url": self.request.GET.get("redirect_url", ""),
            }
        )
        return context

    def get_success_url(self):
        redirect_url = self.request.POST.get("redirect_url")
        if not redirect_url or redirect_url == self.object.get_absolute_url():
            # redirect_url could point to the object being deleted if the
            # request was made from that object's detail page; in this case we
            # also redirect to a default page.
            redirect_url = reverse("notes:list-notes")
        return redirect_url


class RandomNote(View):
    def get(self, request, *args, **kwargs):
        note = Note.objects.order_by("?").first()
        return render(request, "notes/random_note.html", {"note": note})


class DrillNotes(View):
    def get(self, request, *args, **kwargs):
        """Display the Drill start page"""

        notes_count = Note.objects.count()
        disable_begin = bool(notes_count < 2)
        recent_drill_count = Note.objects.filter(
            last_drilled__gt=timezone.now() - timezone.timedelta(hours=24)
        ).count()

        return render(
            request,
            "notes/drill_notes.html",
            {
                "disable_begin": disable_begin,
                "recent_drill_count": recent_drill_count,
            },
        )

    @staticmethod
    def generate_weights(promotion_statuses):
        """Generate a list of weights for use in random selection.

        The return value is intended for use with `random.choices()`. Larger
        weights are given to items toward the end of a sequence of objects,
        but items can also be promoted to increase their chances of being
        drawn.

        :param promotion_statuses: A sequence of boolean values representing
            the promotion (prioritization) status of the corresponding item in
            the sequence of objects from which a selection is to be made.
        """
        n = len(promotion_statuses)
        # By default, weights are drawn from a standard power function
        # distribution with parameter `p`:
        p = 5
        weights = [p * ((x / n) ** (p - 1)) for x in range(1, n + 1)]
        # Promoted items have weights drawn from a linear function:
        for index in itertools.compress(range(n), promotion_statuses):
            weights[index] = p * ((index + 1) / n)
        return weights

    def post(self, request, *args, **kwargs):
        """Run a Drill (do a 'draw'), and also process any pro-/demotion"""

        # ---------------------------------------
        # Perform promotion/demotion if requested
        # ---------------------------------------

        if promote_code := request.POST.get("promote"):
            Note.objects.filter(code=promote_code).update(promoted=True)
        if demote_code := request.POST.get("demote"):
            Note.objects.filter(code=demote_code).update(promoted=False)

        # -----------------------
        # Prepare inputs for draw
        # -----------------------

        values = Note.objects.order_by("-last_drilled").values_list("id", "promoted")
        unzipped_values = tuple(zip(*values))
        # Collection must have at least two notes:
        if not unzipped_values or len(unzipped_values[0]) < 2:
            return render(
                request, "notes/drill_notes.html", {"error": "insufficient-collection"}
            )
        # Latest drilled note should not be picked, hence `[1:]`:
        note_ids = unzipped_values[0][1:]
        promoted_vals = unzipped_values[1][1:]

        # ----------------
        # Perform the draw
        # ----------------

        weights = self.generate_weights(promoted_vals)
        draw_index = random.choices(range(len(weights)), weights)[0]

        # ------------------------------------
        # Update the drawn note's last_drilled
        # ------------------------------------

        Note.objects.filter(id=note_ids[draw_index]).update(last_drilled=timezone.now())

        # --------------------------------------
        # Fetch context data, and finally render
        # --------------------------------------

        note = Note.objects.get(id=note_ids[draw_index])
        recent_drill_count = Note.objects.filter(
            last_drilled__gt=timezone.now() - timezone.timedelta(hours=24)
        ).count()
        return render(
            request,
            "notes/drill_notes.html",
            {
                "note": note,
                "recent_drill_count": recent_drill_count,
            },
        )
