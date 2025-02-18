# Maintainer: D. Can Celasun <can[at]dcc[dot]im>
# Contributor: Ezekiel Bethel <mctinfoilball@gmail.com>

_pkgname=VNTools
pkgname=vntools-git
pkgver=2.0.e5bf961
pkgrel=1
pkgdesc="Collection of tools used by VienDesu! Porting Team"
arch=("any")
url="https://github.com/VienDesuPorting/VNTools"
depends=("python" "python-pillow" "python-pillow-avif-plugin" "python-python-ffmpeg" "python-progress" "python-colorama")
makedepends=("python-setuptools" "git")
provides=("vntools")
source=("git+${url}.git#branch=testing")
sha256sums=("SKIP")

pkgver() {
  cd "${srcdir}/${_pkgname}"
  printf "2.0.%s" "$(git rev-parse --short HEAD)"
}

build() {
  cd "${srcdir}/${_pkgname}"
  python -m build --wheel --no-isolation
}

package() {
  cd "${srcdir}/${_pkgname}"
  python -m installer --destdir="${pkgdir}" dist/*.whl
}

