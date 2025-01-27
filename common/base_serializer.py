import base64
import secrets

from django.core.files.base import ContentFile
from rest_framework import serializers

from utils.custom_datetime import get_formatted_current_time


class CustomBaseSerializer(serializers.ModelSerializer):
    @staticmethod
    def update_related_objects(instance, data_list, model, foreign_key_name=None, user=None, required_decode=False):
        for data in data_list:
            obj_id = data.get('id')
            if required_decode and "file" in data:
                file_format, file_str = data["file"].split(';base64,')
                file_extension = file_format.split('/')[-1]
                file_data = base64.b64decode(file_str)
                file_name = f'{secrets.token_hex(8)}.{file_extension}'
                data["file"] = ContentFile(file_data, name=file_name)

            if obj_id:
                try:
                    obj_instance = model.objects.get(id=obj_id)
                    data["updated_by"] = user
                    data["updated_on"] = get_formatted_current_time()

                    is_delete = data.pop("is_delete", False)
                    if is_delete:
                        obj_instance.delete(deleted_by=user)
                        continue

                    for attr, value in data.items():
                        setattr(obj_instance, attr, value)
                    obj_instance.save()
                except model.DoesNotExist:
                    continue
            else:
                if foreign_key_name:
                    data[foreign_key_name] = instance
                if user:
                    data['created_by'] = user

                model.objects.create(**data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if 'is_delete' in representation:
            del representation['is_delete']

        for key, value in representation.items():
            if value is None:
                representation[key] = ""
            if value == 1:
                representation[key] = 1
            elif value == 0:
                representation[key] = 0
            elif key == "created_by":
                representation[key] = instance.get_created_user()
            elif key == "updated_by":
                representation[key] = instance.get_updated_user()
        return representation
