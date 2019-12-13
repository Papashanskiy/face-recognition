import click
import os
import environ
import logging

env = environ.Env(
    VIDEO_SOURCE=(str, '0'),
    GRAYSCALE=(bool, False),
    URL=(str, 'https://vision-api.invitronet.ru/detection/process/image'),
    CAMERA_ID=(str, None),
    LOGLEVEL=(str, 'INFO')
)


@click.group()
def cli():
    pass


@click.command()
@click.option("-i", "--input", type=str, help="input video file", default=env('VIDEO_SOURCE'))
@click.option("-g", "--grayscale", type=bool, default=env('GRAYSCALE'), help="grayscale")
@click.option("-r", "--rotate", type=float, default=env('ROTATE', cast=float, default=None), help="rotate image angle")
@click.option("-a", "--sample-rate", type=int, default=env('SKIP_SAMPLES', cast=int, default=None), help="A sort of sample rate")
@click.option("-s", "--resize", type=int, default=env('RESIZE_WIDTH', cast=int, default=None), help="resize image width")
@click.option("--crop", type=str, default=env('CROP', cast=str, default=None), help="crop X1xY1xX2xY2")
@click.option("-f", "--forever", type=bool, default=False, required=False, help="auto restart")
@click.option("--url", type=str, default=env('URL'), required=True, help="Image receiver URL (object detector)")
@click.option("--camera-id", type=str, default=env('CAMERA_ID'), required=True, help="Camera ID")
@click.option("--log-level", type=str, default=env('LOGLEVEL'), required=False, help="INFO, DEBUG")
def run(input, grayscale, rotate, sample_rate, resize, forever, url, camera_id, crop, log_level):
    from camera_ocean import app
    args = {'input': input,
            'grayscale': grayscale,
            'rotate': rotate,
            'sample_rate': sample_rate,
            'resize': resize,
            'url': url,
            'forever': forever,
            'camera_id': camera_id,
            'crop': crop}

    logging.basicConfig(
        level=getattr(logging, log_level.upper(), 'DEBUG'),
        format='%(asctime)s %(levelname)s %(module)s %(process)d %(message)s'
    )
    logging.info('run app args={}'.format(args))
    app.run(args=args)


cli.add_command(run)


if __name__ == '__main__':
    cli()
