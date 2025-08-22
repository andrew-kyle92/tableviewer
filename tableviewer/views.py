import json

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.http import JsonResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import View, ListView, DetailView, UpdateView
from django.core.paginator import Paginator
from django.conf import settings

from tableviewer.forms import TableModelForm
from tableviewer.models import DynamicTable, TableColumn, URLShortcut, TableSettings
from .utils import get_column_name, regenerate_table_columns

from .utils.utils import get_file_data, save_columns, search_data, TOP_BANNER_MESSAGES, _save_table_settings


class IndexView(LoginRequiredMixin, View):
    template_name = 'tableviewer/index.html'
    title = 'Table Viewer'

    def get(self, request):
        context = {
            'title': self.title
        }
        return render(request, self.template_name, context)


class AddTableView(LoginRequiredMixin, View):
    template_name = 'tableviewer/add_table.html'
    title = 'Add Table'

    def get(self, request):
        form = TableModelForm()
        context = {
            'form': form,
            'title': self.title,
            "action": "Add",
        }
        return render(request, self.template_name, context)

    def post(self, request):
        form = TableModelForm(request.POST, request.FILES)
        if form.is_valid():
            # saving initial table
            form.save()
            # adding auto-generated columns
            added_columns = save_columns(form.instance)
            if added_columns:
                return redirect(reverse_lazy('table-detail', kwargs={'pk': form.instance.id}))
            else:
                messages.error(request, "Error adding columns to table.")
                return redirect(reverse_lazy('table-detail', kwargs={'pk': form.instance.id}))
        else:
            context = {
                'form': form,
                'title': self.title,
            }
            return render(request, AddTableView.template_name, context)


class EditTableView(LoginRequiredMixin, UpdateView):
    template_name = "tableviewer/add_table.html"
    model = DynamicTable
    form_class = TableModelForm
    success_url = None

    def get_context_data(self, **kwargs):
        context = super(EditTableView, self).get_context_data(**kwargs)
        context["action"] = "Edit"
        context["title"] = "Edit Table: " + self.object.name
        return context

    def get_success_url(self):
        return reverse_lazy('tableviewer:table-detail', kwargs={'pk': self.object.id})


class TablesListView(LoginRequiredMixin, ListView):
    template_name = "tableviewer/tables_list.html"
    model = DynamicTable
    sort_by = '-id'

    def get_context_data(self, **kwargs):
        context = super(TablesListView, self).get_context_data(**kwargs)
        context["title"] = "All Tables"
        return context


class TableDetailView(LoginRequiredMixin, DetailView):
    template_name = "tableviewer/table_detail.html"
    model = DynamicTable

    def get_context_data(self, **kwargs):
        context = super(TableDetailView, self).get_context_data(**kwargs)
        context["title"] = "Table: " + self.object.name
        context["data"] = get_file_data(self.object)
        context["domain_name"] = settings.DOMAIN_NAME
        if not self.object.settings.published:
            context["banner"] = TOP_BANNER_MESSAGES["unpublished"]
        return context


class TableView(LoginRequiredMixin, View):
    template_name = "tableviewer/table_view.html"
    title = ""

    def get(self, request, table_id=None, shortcut=None):
        # url params
        is_preview = request.GET.get('preview', None)

        if table_id:
            table = get_object_or_404(DynamicTable, pk=table_id)
        elif shortcut:
            table = get_object_or_404(DynamicTable, shortcuts__url=shortcut.strip('/'))
        else:
            raise Http404("Table not found.")

        if not table.settings.published and not is_preview:
            raise Http404("This content has moved or no longer exists.")
        else:
            table_data = get_file_data(table, active_only=True)
            self.title = table.name
            paginator = Paginator(table_data["rows"], table.results_shown)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            context = {
                'title': self.title,
                'table': table,
                'table_data': table_data,
                'page_obj': page_obj,
                'is_preview': is_preview
            }
            return render(request, self.template_name, context)


class SearchTable(LoginRequiredMixin, View):
    template_name = "tableviewer/table_view.html"
    title = ""

    def get(self, request, table_id=None, shortcut=None):
        if table_id:
            table = get_object_or_404(DynamicTable, pk=table_id)
        elif shortcut:
            table = get_object_or_404(DynamicTable, shortcuts__url=shortcut.strip('/'))
        else:
            raise Http404("Table not found.")

        # redirecting if the keyword is none
        if request.GET.get('s') == '':
            return redirect(reverse_lazy('tableviewer:table-view', kwargs={'table_id': table_id}))

        # finding the getting the table data
        table_data = get_file_data(table, active_only=True, active_column_header_type="name")
        # getting the search results
        keyword = request.GET.get('s')
        column = request.GET.get('c', None)
        is_preview = request.GET.get('preview', None)
        if column == '':
            column = None
        # getting the csv column name from the label (c)
        if column is not None:
            column = get_column_name(table, column)

        results = search_data(table_data, keyword, column)
        # setting the pagination data
        paginator = Paginator(results, 5)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        # setting the page title
        self.title = table.name
        context = {
            'title': self.title,
            'table': table,
            'table_data': table_data,
            'page_obj': page_obj,
            'url_params': f"s={keyword}&c={request.GET.get('c')}",
            "is_preview": is_preview
        }
        return render(request, self.template_name, context)


# ********** Fetch Requests **********
def save_column(request):
    form_data = json.loads(request.body)
    try:
        column_instance = TableColumn.objects.filter(pk=form_data["id"])
        form_data.pop('id')
        column_instance.update(**form_data)
        return JsonResponse(json.dumps({"results": {"data": column_instance[0].to_json(), "success": True}}), safe=False)
    except IntegrityError as e:
        return JsonResponse(json.dumps({'errors': str(e)}))
    except TableColumn.DoesNotExist:
        return JsonResponse(json.dumps({"errors": "Column does not exist"}))


def regenerate_columns(request, table_id):
    instance = DynamicTable.objects.get(pk=table_id)
    columns = instance.columns.all()
    try:
        regenerate_table_columns(columns, instance)
        return JsonResponse(json.dumps({"success": True}), safe=False)
    except IntegrityError as e:
        return JsonResponse(json.dumps({'errors': str(e), 'success': False}), safe=False)


def add_url_shortcut(request, table_id):
    table_instance = DynamicTable.objects.get(pk=table_id)
    url = request.GET.get('shortcut', None)
    if url is not None:
        try:
            url_instance = URLShortcut(
                table=table_instance,
                url=url
            )
            url_instance.save()
            url_instance_dict = url_instance.__dict__  # getting dictionary values
            url_instance_dict.pop("_state")  # removing the _state key
            return JsonResponse(json.dumps({"success": True, "instance": url_instance_dict}), safe=False)
        except IntegrityError as e:
            return JsonResponse(json.dumps({'error': str(e), 'success': False}), safe=False)
    else:
        return JsonResponse(json.dumps({"error": "Please provide a URL", "success": False}), safe=False)


def remove_url_shortcut(request):
    shortcut_id = request.GET.get('shortcutId', None)
    if shortcut_id is not None:
        try:
            shortcut = URLShortcut.objects.get(pk=shortcut_id)
            shortcut.delete()
            return JsonResponse(json.dumps({"success": True}), safe=False)
        except DynamicTable.DoesNotExist:
            return JsonResponse(json.dumps({"error": "No such shortcut", "success": False}), safe=False)
    else:
        return JsonResponse(json.dumps({"error": "Please provide a URL", "success": False}), safe=False)



def get_domain_name(request):
    return JsonResponse(json.dumps({"domainName": settings.DOMAIN_NAME}), safe=False)


def save_table_settings(request):
    form_data = json.loads(request.body)
    try:
        table_instance = TableSettings.objects.get(pk=form_data.pop("id"))
        _save_table_settings(table_instance, form_data)
        updated_table_instance = TableSettings.objects.get(pk=table_instance.id)
        table_dict = updated_table_instance.__dict__
        table_dict.pop("_state")
        return JsonResponse(json.dumps({"data": table_dict, "success": True}), safe=False)
    except IntegrityError as e:
        return JsonResponse(json.dumps({'error': str(e)}))
    except TableSettings.DoesNotExist:
        return JsonResponse(json.dumps({"error": "Table does not exist"}))
