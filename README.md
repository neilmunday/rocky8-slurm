# rocky8-slurm

[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/neilmunday/rocky8-slurm/docker-image.yml)](https://github.com/neilmunday/rocky8-slurm/actions/workflows/docker-image.yml) [![GitHub issues](https://img.shields.io/github/issues/neilmunday/rocky8-slurm)](https://github.com/neilmunday/rocky8-slurm/issues) [![GitHub license](https://img.shields.io/github/license/neilmunday/rocky8-slurm)](https://github.com/neilmunday/rocky8-slurm/blob/main/LICENSE)

Source repository: https://www.github.com/neilmunday/rocky8-slurm

A Rocky 8 Docker image with a working Slurm installation. This image is intended to allow tests to be performed against a Slurm version.

At present there are no persistent volumes so each invocation of the image creates a clean set-up.

## Pulling

```
docker pull ghcr.io/neilmunday/rocky8-slurm:latest
```

## Building

Use the `SLURM_VER` build argument to specify the Slurm version to build in the image, e.g.

```
docker build  -t  ghcr.io/neilmunday/rocky8-slurm:23.02.2 -t ghcr.io/neilmunday/rocky8-slurm:latest .
```

The default value is currently 23.02.2.

**Note:** The first release of a Slurm version does not require `-1` in the `SLURM_VER` value.

## Running

### Interactive

Run the container in interactive mode:

```
docker run -it --name slurm ghcr.io/neilmunday/rocky8-slurm /bin/bash
```

### Detached

Run the container in detached mode:

```
docker run -d --name slurm ghcr.io/neilmunday/rocky8-slurm
```

Check that the container started ok:

```
docker logs slurm
```

Then you can run commands inside the container like so:

```
docker exec slurm sinfo
```

To submit a job:

```
docker exec -i slurm sbatch < myjob.sh
```
