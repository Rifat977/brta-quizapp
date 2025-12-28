from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import Quiz, Question, Option


class OptionInline(TabularInline):
    """Inline admin for Options"""
    model = Option
    extra = 4
    fields = ('text', 'is_correct', 'order')
    ordering = ('order',)


class QuestionInline(TabularInline):
    """Inline admin for Questions"""
    model = Question
    extra = 1
    fields = ('text', 'image', 'order')
    ordering = ('order',)
    show_change_link = True


@admin.register(Quiz)
class QuizAdmin(ModelAdmin):
    """Admin interface for Quiz model"""
    list_display = ('title', 'time_limit', 'get_total_questions', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'description')
    fields = ('title', 'description', 'time_limit', 'is_active')
    inlines = [QuestionInline]
    
    def get_total_questions(self, obj):
        return obj.get_total_questions()
    get_total_questions.short_description = 'Total Questions'


@admin.register(Question)
class QuestionAdmin(ModelAdmin):
    """Admin interface for Question model"""
    list_display = ('text', 'quiz', 'order', 'has_image', 'get_options_count', 'created_at')
    list_filter = ('quiz', 'created_at')
    search_fields = ('text', 'quiz__title')
    fields = ('quiz', 'text', 'image', 'order')
    ordering = ('quiz', 'order')
    inlines = [OptionInline]
    
    def has_image(self, obj):
        """Check if question has an image"""
        return bool(obj.image)
    has_image.boolean = True
    has_image.short_description = 'Has Image'
    
    def get_options_count(self, obj):
        return obj.options.count()
    get_options_count.short_description = 'Options'


@admin.register(Option)
class OptionAdmin(ModelAdmin):
    """Admin interface for Option model"""
    list_display = ('text', 'question', 'is_correct', 'order')
    list_filter = ('is_correct', 'question__quiz')
    search_fields = ('text', 'question__text')
    fields = ('question', 'text', 'is_correct', 'order')
    ordering = ('question', 'order')
