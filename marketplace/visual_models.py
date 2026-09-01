from django.db import models


class ProductReference(models.Model):
    """Canonical visual reference for a real product/model known by UZA."""
    category = models.ForeignKey('marketplace.Category', on_delete=models.PROTECT, related_name='visual_references')
    brand = models.CharField(max_length=120)
    model = models.CharField(max_length=180)
    reference = models.CharField(max_length=120, blank=True)
    aliases = models.JSONField(default=list, blank=True)
    visual_features = models.JSONField(default=dict, blank=True)
    verified = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['brand', 'model'], name='uza_unique_visual_product')]
        indexes = [models.Index(fields=['category', 'brand']), models.Index(fields=['brand', 'model'])]

    def __str__(self):
        return f'{self.brand} {self.model}'


class ProductReferenceImage(models.Model):
    reference = models.ForeignKey(ProductReference, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='visual_reference/%Y/%m/')
    view = models.CharField(max_length=40, blank=True)
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=['reference', 'approved'])]


class VisualEmbedding(models.Model):
    image = models.OneToOneField(ProductReferenceImage, on_delete=models.CASCADE, related_name='embedding')
    vector = models.BinaryField()
    dimensions = models.PositiveIntegerField()
    model_name = models.CharField(max_length=180)
    index_position = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class RecognitionResult(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)
    category = models.CharField(max_length=120, blank=True)
    confidence = models.FloatField(default=0)
    status = models.CharField(max_length=30, default='READY')
    engine = models.CharField(max_length=80, default='LOCAL')
    created_at = models.DateTimeField(auto_now_add=True)


class RecognitionCandidate(models.Model):
    result = models.ForeignKey(RecognitionResult, on_delete=models.CASCADE, related_name='candidates')
    reference = models.ForeignKey(ProductReference, on_delete=models.SET_NULL, null=True, blank=True)
    score = models.FloatField(default=0)
    rank = models.PositiveIntegerField(default=1)
    evidence = models.JSONField(default=dict, blank=True)


class RecognitionFeedback(models.Model):
    result = models.ForeignKey(RecognitionResult, on_delete=models.CASCADE, related_name='feedback')
    reference = models.ForeignKey(ProductReference, on_delete=models.SET_NULL, null=True, blank=True)
    decision = models.CharField(max_length=30, choices=[('CORRECT', 'Correct'), ('WRONG', 'Incorrect'), ('NEW', 'Nouveau modèle')])
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
