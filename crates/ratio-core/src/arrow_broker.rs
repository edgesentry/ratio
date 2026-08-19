//! Memory Broker: shareable-product rows as Arrow (not raw waveforms).

use std::sync::Arc;

use arrow::array::{ArrayRef, BooleanArray, StringArray};
use arrow::datatypes::{DataType, Field, Schema};
use arrow::error::ArrowError;
use arrow::ipc::writer::StreamWriter;
use arrow::record_batch::RecordBatch;

use crate::product::ShareableProduct;

pub fn products_to_record_batch(products: &[ShareableProduct]) -> Result<RecordBatch, ArrowError> {
    let schema = Arc::new(Schema::new(vec![
        Field::new("device_id", DataType::Utf8, false),
        Field::new("ts", DataType::Utf8, false),
        Field::new("scenario", DataType::Utf8, false),
        Field::new("result", DataType::Utf8, false),
        Field::new("raw_data_pointer", DataType::Utf8, true),
        Field::new("product_json", DataType::Utf8, false),
        Field::new("envelope_ok", DataType::Boolean, false),
    ]));

    let mut device_id = Vec::with_capacity(products.len());
    let mut ts = Vec::with_capacity(products.len());
    let mut scenario = Vec::with_capacity(products.len());
    let mut result = Vec::with_capacity(products.len());
    let mut pointers: Vec<Option<String>> = Vec::with_capacity(products.len());
    let mut product_json = Vec::with_capacity(products.len());
    let mut envelope_ok = Vec::with_capacity(products.len());

    for p in products {
        device_id.push(p.source_device.clone());
        ts.push(p.timestamp.clone());
        scenario.push(p.scenario.clone());
        result.push(
            p.inference
                .get("result")
                .and_then(|v| v.as_str())
                .unwrap_or("")
                .to_string(),
        );
        pointers.push(
            p.data_governance
                .get("rawDataPointer")
                .and_then(|v| v.as_str())
                .map(str::to_string),
        );
        let value = p
            .to_value()
            .map_err(|e| ArrowError::ComputeError(e.to_string()))?;
        product_json.push(
            serde_json::to_string(&value).map_err(|e| ArrowError::ComputeError(e.to_string()))?,
        );
        envelope_ok.push(crate::envelope::validate_envelope(&value).is_ok());
    }

    RecordBatch::try_new(
        schema,
        vec![
            Arc::new(StringArray::from(device_id)) as ArrayRef,
            Arc::new(StringArray::from(ts)),
            Arc::new(StringArray::from(scenario)),
            Arc::new(StringArray::from(result)),
            Arc::new(StringArray::from(pointers)),
            Arc::new(StringArray::from(product_json)),
            Arc::new(BooleanArray::from(envelope_ok)),
        ],
    )
}

pub fn record_batch_to_ipc(batch: &RecordBatch) -> Result<Vec<u8>, ArrowError> {
    let mut buf = Vec::new();
    {
        let mut writer = StreamWriter::try_new(&mut buf, batch.schema().as_ref())?;
        writer.write(batch)?;
        writer.finish()?;
    }
    Ok(buf)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::product::{build_shareable_product, DeriveInput, Scenario};
    use arrow::ipc::reader::StreamReader;
    use std::io::Cursor;

    #[test]
    fn ipc_roundtrip_has_no_raw_column() {
        let product = build_shareable_product(&DeriveInput::stub_for(
            Scenario::K1,
            "urn:uuid:00000000-0000-0000-0000-000000000001",
            "2026-08-18T00:00:00Z",
            "local://storage/K1/raw_wave.bin",
        ))
        .unwrap();
        let batch = products_to_record_batch(&[product]).unwrap();
        assert_eq!(batch.num_rows(), 1);
        assert!(batch.schema().field_with_name("waveform").is_err());
        let ipc = record_batch_to_ipc(&batch).unwrap();
        let reader = StreamReader::try_new(Cursor::new(ipc), None).unwrap();
        let back = reader.into_iter().next().unwrap().unwrap();
        assert_eq!(back.num_rows(), 1);
        let ptr = back
            .column_by_name("raw_data_pointer")
            .unwrap()
            .as_any()
            .downcast_ref::<StringArray>()
            .unwrap()
            .value(0);
        assert!(ptr.starts_with("local://"));
    }
}
