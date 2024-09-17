PROJECT_NAME_HYPHEN=pyshiny-quarto-example
PROJECT_NAME_UNDERSCORE=pyshiny_quarto_example


.PHONY: deps # Install dependencies into the current python environment.
deps: 
	pip install -r requirements.txt

.PHONY: pyenv # Create a python environment and set it to the active directory.
pyenv:
	pyenv virtualenv-delete $(PROJECT_NAME_HYPHEN) || true
	pyenv virtualenv 3.9.13 $(PROJECT_NAME_HYPHEN)
	pyenv local $(PROJECT_NAME_HYPHEN)

.PHONY: run # Run the shiny app
run:
	shiny run

.PHONY: deploy-shinyappsio # Deploy to staging.shinyapps io
deploy-shinyappsio:
	rsconnect deploy shiny . --name perman --title pyshiny-quarto-example

.PHONY: deploy-cloud # Deploy to staging.posit.cloud
deploy-cloud:
	rsconnect deploy shiny . --name cloud-staging --title pyshiny-quarto-example

.PHONY: deploy-shinyappsio-prod # Deploy to shinyapps io
deploy-shinyappsio-prod:
	rsconnect deploy shiny . --name perman-prod --title pyshiny-quarto-example

.PHONY: deploy-cloud-prod # Deploy to posit.cloud
deploy-cloud-prod:
	rsconnect deploy shiny . --name cloud-prod --title pyshiny-quarto-example

.PHONY: clean # Clean the directory.
clean:
	find . \( -name '*.pyc' -or -name '*.pyo' \) -print -delete
	find . -name '__pycache__' -print -delete
