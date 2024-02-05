GLOTLIB_VERS := 0.9.4
MODULES := \
	setup.cfg \
	setup.py \
	glotlib/shaders/*.py \
	glotlib/shaders/*.frag \
	glotlib/shaders/*.vert \
	glotlib/font_files/*.py \
	glotlib/font_files/ttf_bitstream_vera_1_10/* \
	glotlib/*.py
PYTHON := python3

.PHONY: all
all: glotlib

.PHONY: clean
clean:
	rm -rf dist *.egg-info build
	find . -name "*.pyc" | xargs rm 2>/dev/null || true
	find . -name __pycache__ | xargs rm -r 2>/dev/null || true

.PHONY: test
test: flake8 lint

.PHONY: flake8
flake8:
	$(PYTHON) -m flake8 glotlib tests

.PHONY: lint
lint:
	$(PYTHON) -m pylint -j2 glotlib tests

.PHONY: glotlib
glotlib: dist/glotlib-$(GLOTLIB_VERS)-py3-none-any.whl

.PHONY: install
install: glotlib | uninstall
	sudo $(PYTHON) -m pip install dist/glotlib-$(GLOTLIB_VERS)-py3-none-any.whl

.PHONY: uninstall
uninstall:
	sudo $(PYTHON) -m pip uninstall -y glotlib

.PHONY: publish
publish: glotlib
	$(PYTHON) -m twine upload \
		dist/glotlib-$(GLOTLIB_VERS)-py3-none-any.whl \
		dist/glotlib-$(GLOTLIB_VERS).tar.gz

dist/glotlib-$(GLOTLIB_VERS)-py3-none-any.whl: $(MODULES) Makefile
	$(PYTHON) -m build
	$(PYTHON) -m twine check $@
