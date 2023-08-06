import csv
import io

from rest_framework import renderers

DATA_FILE_HEADERS = [
    'Ингредиент',
    'Количество',
    'Единицы_измерения',
]


class CSVDataRenderer(renderers.BaseRenderer):

    media_type = "text/csv"
    format = "csv"

    def render(self, data, accepted_media_type=None, renderer_context=None):

        csv_buffer = io.StringIO()
        csv_writer = csv.DictWriter(
            csv_buffer, fieldnames=DATA_FILE_HEADERS, extrasaction="ignore"
        )
        csv_writer.writeheader()

        for ingredient_data in data:
            csv_writer.writerow(ingredient_data)

        return csv_buffer.getvalue()


class TextDataRenderer(renderers.BaseRenderer):

    media_type = "text/plain"
    format = "txt"

    def render(self, data, accepted_media_type=None, renderer_context=None):

        text_buffer = io.StringIO()
        text_buffer.write(
            ' '.join(header for header in DATA_FILE_HEADERS) + '\n'
        )

        for student_data in data:
            text_buffer.write(
                ' '.join(str(sd) for sd in list(student_data.values())) + '\n'
            )

        return text_buffer.getvalue()
