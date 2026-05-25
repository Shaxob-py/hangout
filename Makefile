mig:
	alembic revision --autogenerate -m "update"
	 alembic upgrade head

start:
	docker start 48944fd802ab
	docker start 48944fd802ab