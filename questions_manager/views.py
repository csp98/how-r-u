from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.db.models import Q
from .models import Question, Doctor
# Create your views here.
from .forms import CreateQuestionForm, QuestionForm, DeleteQuestionForm


@login_required(login_url="/login/")
def create(request):
    if request.method == 'POST':
        # Create a form instance and populate it with data from the request (binding):
        form = CreateQuestionForm(request.POST)
        if form.is_valid():
            question = Question(text=form.cleaned_data.get("text"),
                                responses=form.cleaned_data.get("responses"),
                                public=form.cleaned_data.get("public"),
                                creator_id=request.user.doctor,
                                language=form.cleaned_data.get("language"))
            question.save()
            question.doctor_set.add(request.user.doctor)
            question.save()
            return my_questions(request, new_context={"success_msg": "Question has been successfully created"})
    else:
        form = CreateQuestionForm()
    context = {
        'form': form,
    }
    return render(request, 'questions_manager/create.html', context)


@login_required(login_url="/login/")
def my_questions(request, new_context={}):
    questions = request.user.doctor.assigned_questions.all()
    context = {
        'questions': questions,
    }
    context.update(new_context)
    return render(request, 'questions_manager/my_questions.html', context)

@login_required(login_url="/login/")
def public_questions(request, new_context={}):
    doctor = Doctor.objects.get(user=request.user)
    questions = Question.objects.filter(
       # ~Q(creator_id=doctor) &
        Q(public=True)
    )
    context = {
        'questions': questions,
    }
    context.update(new_context)
    return render(request, 'questions_manager/public_questions.html', context)

@login_required(login_url="/login/")
def assign(request, question_id):
    question = Question.objects.get(id=question_id)
    question.doctor_set.add(request.user.doctor)
    question.save()
    context = {
        "success_msg": "Question has been successfully assigned"
    }
    return public_questions(request, context)

@login_required(login_url="/login/")
def delete(request, question_id):
    question = Question.objects.get(id=question_id)
    context = {"question": question}
    if request.method == "POST":
        form = DeleteQuestionForm(request.POST)
        if form.is_valid():
            delete_question = form.cleaned_data['delete_for_others']
            request.user.doctor.assigned_questions.remove(question)
            if delete_question:
                Question.objects.get(id=question_id).delete()
            return my_questions(request, new_context={"success_msg": "Question has been successfully deleted"})
    return render(request, 'questions_manager/delete.html', context)


@login_required(login_url="/login/")
def modify(request, question_id):
    if request.method == "POST":
        form = QuestionForm(request.POST, instance=Question.objects.get(id=question_id))
        if form.is_valid():
            form.instance.responses = form.cleaned_data.get('responses')
            form.save()
            return my_questions(request, new_context={"success_msg": "Question has been successfully modified"})
    else:
        form = QuestionForm(instance=Question.objects.get(id=question_id))
    return render(request, 'questions_manager/modify.html', context={"form": form})
