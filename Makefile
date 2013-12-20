CONFIG=babel.cfg
MESSAGES=messages.pot
TRANSLATIONS=brew/translations
ALL_LINGUAS=cs de
POFILES=$(shell LINGUAS="$(ALL_LINGUAS)"; DIR="$(TRANSLATIONS)"; for lang in $$LINGUAS; do printf "$$DIR/$$lang/LC_MESSAGES/messages.po "; done)
MOFILES=$(patsubst %.po,%.mo,$(POFILES))

.PHONY: createpo init install run updatepo updatepot

all: run

run: $(MOFILES)
	@python manage.py runserver

init:
	@python manage.py populatedb

install:
	@python setup.py install

createpo: $(MESSAGES)
	@echo "\n>>> Enter language code"; read lang_code; pybabel init -i $(MESSAGES) -d $(TRANSLATIONS) -l $$lang_code

updatepo: $(MESSAGES)
	@pybabel update -i $(MESSAGES) -d $(TRANSLATIONS)

updatepot:
	@pybabel extract -F $(CONFIG) -o $(MESSAGES) .

%.mo: %.po
	@pybabel compile -f -i $< -o $@
