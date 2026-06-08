"""
Knowledge base app models: KnowledgeBaseArticle.
"""

from django.db import models


class KnowledgeBaseArticle(models.Model):
    CATEGORY_CHOICES = [
        ('Best Practices', 'Best Practices'),
        ('Vaccination Schedule', 'Vaccination Schedule'),
        ('Nutrition', 'Nutrition'),
    ]

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    body = models.TextField()
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category', 'title']

    def __str__(self):
        return self.title
