from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import hashlib


class Project(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    # Relationship to the user(s) invited as collaborators
    collaborators = models.ManyToManyField(
        User,
        through="ProjectCollaborator",  # Use intermediate model for additional information
        related_name="projects",
    )

    def save_new_version(self):
        """
        Save changes as a new version in the ProjectVersion model.
        """
        new_version = ProjectVersion.objects.create(
            project=self,
            name=self.name,
            description=self.description,
        )
        return new_version

    def get_history(self):
        """
        Retrieve the entire history of changes for this project.
        """
        return ProjectVersion.objects.filter(project=self).order_by("-created_at")

    def __str__(self):
        return f"{self.name} (Updated: {self.updated_at})"


class ProjectVersion(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Version of {self.project.name} (Created: {self.created_at})"


def hash_image(image_path):
    with open(image_path, "rb") as f:
        img_hash = hashlib.sha256()
        while chunk := f.read(8192):
            img_hash.update(chunk)
    return img_hash.hexdigest()


class ProjectImage(models.Model):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(
        upload_to="project_images/"
    )  # Field untuk menyimpan gambar
    image_hash = models.CharField(max_length=64, unique=True)  # Untuk menyimpan hash
    created_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        # Hitung hash sebelum menyimpan
        self.image_hash = hash_image(self.image.path)
        super().save(*args, **kwargs)  # Panggil metode save dari superclass

    def __str__(self):
        return f"Image Hash for {self.project.name} (Uploaded: {self.created_at})"


class ProjectCollaborator(models.Model):
    """
    Intermediate model to store information about each collaborator.
    """

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    invited_at = models.DateTimeField(default=timezone.now)
    is_accepted = models.BooleanField(
        default=False
    )  # Whether the invite has been accepted

    def __str__(self):
        return f"{self.user.username} on {self.project.name} (Accepted: {self.is_accepted})"
