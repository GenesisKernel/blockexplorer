""" The config command. """

from .base import Base, config_editor

class Config(Base):
    """ Configure block explorer """

    def run(self):
        config = config_editor.ConfigEditor(self.config_path)

        sqla_binds = self.options.get("--set-sqla-binds")
        backend_api_urls = self.options.get("--set-backend-api-urls")
        db_engines = self.options.get("--set-db-engines")
        aux_db_engines = self.options.get("--set-aux-db-engines")
        redis_url = self.options.get("--set-redis-url")
        celery_broker_url = self.options.get("--set-celery-broker-url")
        celery_result_backend = self.options.get("--set-celery-result-backend")
        socketio_host = self.options.get("--set-socketio-host")
        socketio_port = self.options.get("--set-socketio-port")
        enable_database_selector = self.options.get("--set-enable-database-selector")
        enable_database_explorer = self.options.get("--set-enable-database-explorer")
        product_brand_name =  self.options.get("--set-product-brand-name")

        config_parsed = False
        if sqla_binds or backend_api_urls or db_engines or aux_db_engines \
                or redis_url or celery_broker_url or celery_result_backend \
                or enable_database_selector or enable_database_explorer \
                or socketio_host or socketio_port or product_brand_name:
            config_parsed = True
            config.parse()

        if sqla_binds:
            config.parsed.set_sqla_binds(sqla_binds)

        if backend_api_urls:
            config.parsed.set_backend_api_urls(backend_api_urls)

        if db_engines:
            config.parsed.set_db_engines(db_engines)

        if aux_db_engines:
            config.parsed.set_aux_db_engines(aux_db_engines)

        if redis_url:
            config.parsed.set_redis_url(redis_url)

        if celery_broker_url:
            config.parsed.set_celery_broker_url(celery_broker_url)

        if celery_result_backend:
            config.parsed.set_celery_result_backend(celery_result_backend)

        if socketio_host:
            config.parsed.set_socketio_host(socketio_host)

        if socketio_port:
            config.parsed.set_socketio_port(socketio_port)

        if enable_database_selector:
            config.parsed.set_enable_database_selector(enable_database_selector)
        if enable_database_explorer:
            config.parsed.set_enable_database_explorer(enable_database_explorer)
        if product_brand_name:
            config.parsed.set_product_brand_name(product_brand_name)

        if config_parsed:
            config.parsed_to_content()
            config.save()
