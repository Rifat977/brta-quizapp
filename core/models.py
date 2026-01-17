from django.db import models
from django.core.validators import MinValueValidator


class Quiz(models.Model):
    """Model representing a quiz/test"""
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    time_limit = models.IntegerField(
        help_text="Time limit in minutes",
        validators=[MinValueValidator(1)]
    )
    language = models.CharField(
        max_length=50,
        default='বাংলা',
        help_text='Language of the quiz'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Quizzes"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_total_questions(self):
        """Returns the total number of questions in this quiz"""
        return self.questions.count()


class Question(models.Model):
    """Model representing a question in a quiz"""
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    text = models.TextField()
    image = models.ImageField(
        upload_to='questions/',
        blank=True,
        null=True,
        help_text="Optional image to display with the question"
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Order of the question in the quiz"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.quiz.title} - Q{self.order + 1}"

    def get_correct_option(self):
        """Returns the correct option for this question"""
        return self.options.filter(is_correct=True).first()


class Option(models.Model):
    """Model representing an option/answer choice for a question"""
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='options'
    )
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(
        default=0,
        help_text="Order of the option in the question"
    )

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.question} - {self.text[:50]}"
