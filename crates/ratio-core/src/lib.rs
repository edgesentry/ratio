//! Thin on-site composition: keep raw bytes in-domain, emit shareable-product metadata.

pub mod arrow_broker;
pub mod custody;
pub mod envelope;
pub mod pointer;
pub mod product;
pub mod queue;
pub mod td;

pub use arrow_broker::{products_to_record_batch, record_batch_to_ipc};
pub use custody::{raw_pointer, write_raw_stub};
pub use envelope::{validate_envelope, EnvelopeError};
pub use pointer::{assert_local_pointer, is_local_pointer, PointerError};
pub use product::{
    build_shareable_product, DeriveError, DeriveInput, Domain, Scenario, ShareableProduct,
};
pub use queue::{dequeue, enqueue, list_queued, load_queued, queue_depth, refresh_depths};
pub use td::{load_td, TdError, ThinTd};

pub const RAW_STUB_MARKER: &str = "RATIO_RAW_STUB";
