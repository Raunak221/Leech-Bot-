#  Copyright (C) 2020 PublicLeech Authors

#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.

#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.

#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

# creates a layer from the base Docker image.
FROM python:3.9.5-slim-buster

# set working directory
WORKDIR /app

# http://bugs.python.org/issue19846
# https://github.com/SpEcHiDe/PublicLeech/pull/97
ENV LANG=C.UTF-8

# sets the TimeZone, to be used inside the container
ENV TZ=Asia/Kolkata

# fix "ephimeral" / "AWS" file-systems
RUN sed -i.bak 's/us-west-2\.ec2\.//' /etc/apt/sources.list

# synchronize the package index files from their sources.
# and install required pre-requisites before proceeding ...
RUN apt-get update \
	&& apt-get install -y \
	software-properties-common \
	&& apt-add-repository non-free

# resynchronize and install required packages
RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
	# this package is required to fetch "contents" via "TLS"
	apt-transport-https \
	# install gcc [ PEP 517 ]
	build-essential gcc \
	# install megatools and dependencies
	megatools jq pv \
	# install encoding tools
	ffmpeg \
	# install extraction tools
	p7zip rar unrar unzip zip \
	# miscellaneous helpers
	curl git procps wget \
	# clean up automatically installed and are no longer required packages
	&& apt-get autoremove && apt-get clean  \
	# clean up the container "layer", after we are done
	&& rm -rf /var/lib/apt/lists
	
# each instruction creates one layer
# Only the instructions RUN, COPY, ADD create layers.
# there are multiple '' dependancies,
# requiring the use of the entire repo, hence
# adds files from your Docker client’s current directory.
COPY . .

# install rclone, aria2 and pip packages via external scripts
RUN bash install-packages.sh

# specifies what command to run within the container.
CMD ["bash", "torrent-leecher.sh"]
