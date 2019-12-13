import click
import settings
import os
from recognition import tasks
from core.image import np_to_jpeg
from core.db import UIPatients


@click.group()
def cli():
    pass


@cli.command()
def clear_database():
    from core.db import ImageMaster, Image, ImageDescriptor
    Image().collection.delete_many({})
    ImageDescriptor().collection.delete_many({})
    ImageMaster().collection.delete_many({})
    UIPatients().patients_collection.delete_many({})


@cli.command()
@click.argument('path', type=click.Path(exists=True, file_okay=False))
def load_images_from_directory(path):
    from detection.app import ImageStore
    from core.db import ImageMaster
    saver = ImageStore()
    masterdb = ImageMaster()

    click.echo('load images from: {}'.format(path))

    def iter_files(path):
        for root, dirs, files in os.walk(path, topdown=False):
            for name in files:
                yield os.path.join(root, name)

    def split_filename(filename):
        parts = os.path.split(filename)
        print(parts)
        if parts[0]:
            return parts[0].split(os.sep)[-1], filename
        else:
            return None, filename

    def save_image_for(filename, subject_id):
        """
        Загружаем картинку filename в базу и отмечаем её как subject_id

        :param filename: путь к картинке
        :param subject_id: id пациента
        :return:
        """
        from detection.extractor import FaceExtractor
        extractor = FaceExtractor(path=filename)

        if subject_id and ' ' in subject_id:
            # Создадим запись в таблице Patients
            name, surname = subject_id.split(' ', 1)
            UIPatients().insert({'name': name, 'surname': surname})

        for data in extractor.iter_frames():
            for face in data['faces']:
                img_bytes = np_to_jpeg(face['image'])
                if not img_bytes:
                    continue
                image_id = saver.save(img_bytes)
                vector = tasks.calc_descriptor(str(image_id), merge=False)
                if vector:
                    master_id = tasks.merge_image(image_id=str(image_id), vector=vector)
                    if master_id:
                        masterdb.set_subject_id(id=master_id, subject_id=subject_id)
                        print(__name__, "set subject_id", master_id, subject_id)


    for filename in iter_files(path):
        subject_id, _ = split_filename(filename)
        if subject_id:
            click.echo('load image {} for subject_id={}'.format(filename, subject_id))
            save_image_for(filename, subject_id=subject_id)
        else:
            click.echo('skip image {}, no subject_id'.format(filename))

if __name__ == '__main__':
    cli()
