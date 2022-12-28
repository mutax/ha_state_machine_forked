"""Config flow for State Machine integration."""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any, cast, Optional

import voluptuous as vol

from homeassistant.core import callback
from homeassistant.const import CONF_ENTITY_ID
from homeassistant.helpers.selector import (
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)
from homeassistant import data_entry_flow, config_entries, core
from homeassistant.helpers.schema_config_entry_flow import (
    SchemaConfigFlowHandler,
    SchemaFlowFormStep,
    SchemaFlowMenuStep,
)
import homeassistant.helpers.config_validation as cv
import logging
import yaml

from .const import DOMAIN

CONF_NAME = "name"
CONF_SCHEMA_YAML = "schema_yaml"

_LOGGER = logging.getLogger(__name__)


def normalize_input(user_input: Optional[dict[str, Any]]) -> dict[str, str]:
    """Validate states"""
    _LOGGER.warning("Validate: %s", user_input)

    errors = {}

    try:
        schema = yaml.safe_load(user_input[CONF_SCHEMA_YAML])
        _LOGGER.warning("Schema: %s", schema)
    except yaml.YAMLError as exc:
        _LOGGER.warning("Schema Error: %s", exc)
        errors["base"] = "schema_parse_error"

    return errors


class StateMachineConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """State Machine config flow."""

    data: dict[str, Any] = {}

    def __init__(self) -> None:
        """Initialize config flow."""
        self.options: dict[str, Any] = {}

    async def async_step_user(self, user_input: Optional[dict[str, Any]] = None):
        """Invoked when a user initiates a flow via the user interface."""
        _LOGGER.warning("Show Setup UI & validate input: %s", user_input)
        errors: dict[str, str] = {}

        if user_input is not None:
            errors = normalize_input(user_input)

            self.options.update(user_input)

            if not errors:
                return self.async_create_entry(
                    title=user_input[CONF_NAME],
                    data={},
                    options=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=_build_setup_schema(self.hass, self.options),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Options Flow Handler"""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        _LOGGER.warning("Init Options UI: %s", config_entry.as_dict())
        self.options = dict(config_entry.options)

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> data_entry_flow.FlowResult:
        """Manage the options."""
        _LOGGER.warning("Show Options UI & validate input: %s", user_input)
        errors: dict[str, str] = {}

        if user_input is not None:
            errors = normalize_input(user_input)

            self.options.update(user_input)

            if not errors:
                return self.async_create_entry(
                    title=self.options[CONF_NAME],
                    data=self.options,
                )

        return self.async_show_form(
            step_id="init",
            data_schema=_build_options_schema__states(self.hass, self.options),
            errors=errors,
        )


def _build_setup_schema(
    hass: core.HomeAssistant, user_input: dict[str, Any]
) -> vol.Schema:
    return vol.Schema(
        {vol.Required(CONF_NAME, default=user_input.get(CONF_NAME)): cv.string}
    ).extend(_build_options_schema__states(hass, user_input).schema)


def _build_options_schema__states(
    hass: core.HomeAssistant, user_input: dict[str, Any]
) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(
                CONF_SCHEMA_YAML, default=user_input.get(CONF_SCHEMA_YAML)
            ): TextSelector(TextSelectorConfig(multiline=True))
        }
    )
