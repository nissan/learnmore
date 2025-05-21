from rest_framework import serializers
from .models import Course, Module, Quiz, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']

class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ['id', 'title', 'instructions']

class ModuleSerializer(serializers.ModelSerializer):
    quizzes = QuizSerializer(many=True)

    class Meta:
        model = Module
        fields = ['id', 'title', 'description', 'order', 'quizzes']

    def validate_quizzes(self, value):
        if len(value) < 1:
            raise serializers.ValidationError("Each module must have at least 1 quiz.")
        return value

class CourseSerializer(serializers.ModelSerializer):
    modules = ModuleSerializer(many=True)
    categories = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), many=True)
    instructor = serializers.StringRelatedField()

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'description', 'instructor', 'categories',
            'difficulty', 'duration', 'is_public', 'created_at', 'modules'
        ]

    def validate_modules(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("A course must have at least 3 modules.")
        return value

    def create(self, validated_data):
        modules_data = validated_data.pop('modules')
        categories = validated_data.pop('categories')
        course = Course.objects.create(**validated_data)
        course.categories.set(categories)
        for module_data in modules_data:
            quizzes_data = module_data.pop('quizzes')
            module = Module.objects.create(course=course, **module_data)
            for quiz_data in quizzes_data:
                Quiz.objects.create(module=module, **quiz_data)
        return course 