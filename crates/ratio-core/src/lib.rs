//! Thin on-site composition: keep raw bytes in-domain, emit shareable-product metadata.

pub mod arrow_broker;
pub mod envelope;
pub mod pointer;
pub mod product;

pub use arrow_broker::{products_to_record_batch, record_batch_to_ipc};
pub use envelope::{validate_envelope, EnvelopeError};
pub use pointer::{assert_local_pointer, is_local_pointer, PointerError};
pub use product::{
    build_shareable_product, DeriveError, DeriveInput, Domain, Scenario, ShareableProduct,
};

pub const RAW_STUB_MARKER: &str = "RATIO_RAW_STUB";
