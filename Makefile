CONFIG=babel.cfg
MESSAGES=messages.pot
TRANSLATIONS_DIR=brew/translations

.PHONY: createpo compilepo init install run updatepot

all: run

run: compilepo
	@python manage.py runserver

init:
	@python manage.py populatedb

createpo: $(MESSAGES)
	@echo "\n>>> Enter language code"; read lang_code; pybabel init -i $(MESSAGES) -d $(TRANSLATIONS_DIR) -l $$lang_code

compilepo: $(MESSAGES)
	@pybabel compile -f -d $(TRANSLATIONS_DIR)

updatepot: $(MESSAGES)
	@pybabel update -i $(MESSAGES) -d $(TRANSLATIONS_DIR)

$(MESSAGES):
	@pybabel extract -F $(CONFIG) -o $(MESSAGES) .
