//! Python prototype bindings. ODS handoff stays in `poc/`; this module derives and splits.

use ::ratio_core::product::{build_shareable_product, DeriveInput, Scenario, ShareableProduct};
use ::ratio_core::{
    assert_local_pointer, is_local_pointer, products_to_record_batch, record_batch_to_ipc,
    validate_envelope, RAW_STUB_MARKER,
};
use pyo3::exceptions::{PyRuntimeError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyModule};
use serde_json::Value;

fn py_err(err: impl std::fmt::Display) -> PyErr {
    PyValueError::new_err(err.to_string())
}

fn scenario_from_str(s: &str) -> PyResult<Scenario> {
    Scenario::parse(s).ok_or_else(|| PyValueError::new_err("scenario must be K1, S1, or S2"))
}

#[pyfunction]
fn local_pointer_ok(pointer: &str) -> bool {
    is_local_pointer(pointer)
}

#[pyfunction]
fn require_local_pointer(pointer: &str) -> PyResult<()> {
    assert_local_pointer(pointer).map_err(py_err)
}

#[pyfunction]
#[pyo3(signature = (scenario, pointer, product_id=None, timestamp=None))]
fn derive_stub_product_json(
    scenario: &str,
    pointer: &str,
    product_id: Option<&str>,
    timestamp: Option<&str>,
) -> PyResult<String> {
    let sc = scenario_from_str(scenario)?;
    let input = DeriveInput::stub_for(
        sc,
        product_id.unwrap_or("urn:uuid:00000000-0000-0000-0000-000000000001"),
        timestamp.unwrap_or("2026-08-18T00:00:00Z"),
        pointer,
    );
    let product = build_shareable_product(&input).map_err(py_err)?;
    product.to_json().map_err(py_err)
}

#[pyfunction]
fn validate_product_json(product_json: &str) -> PyResult<()> {
    let value: Value = serde_json::from_str(product_json).map_err(py_err)?;
    validate_envelope(&value).map_err(py_err)
}

#[pyfunction]
fn products_json_to_arrow_ipc(py: Python<'_>, products_json: &str) -> PyResult<Py<PyBytes>> {
    let values: Vec<ShareableProduct> = serde_json::from_str(products_json).map_err(py_err)?;
    let batch =
        products_to_record_batch(&values).map_err(|e| PyRuntimeError::new_err(e.to_string()))?;
    let ipc = record_batch_to_ipc(&batch).map_err(|e| PyRuntimeError::new_err(e.to_string()))?;
    Ok(PyBytes::new(py, &ipc).unbind())
}

#[pymodule]
fn ratio_core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(local_pointer_ok, m)?)?;
    m.add_function(wrap_pyfunction!(require_local_pointer, m)?)?;
    m.add_function(wrap_pyfunction!(derive_stub_product_json, m)?)?;
    m.add_function(wrap_pyfunction!(validate_product_json, m)?)?;
    m.add_function(wrap_pyfunction!(products_json_to_arrow_ipc, m)?)?;
    m.add("RAW_STUB_MARKER", RAW_STUB_MARKER)?;
    Ok(())
}
