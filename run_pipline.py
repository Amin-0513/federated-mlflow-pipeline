from pipeline.FL_Averaging import FL_Averaging

if __name__ == "__main__":
    data_path =rf"C:\Users\Amin\Desktop\federated server\brain-tumor-mri-dataset"
    model_path="C:\\Users\\Amin\\Desktop\\federated server\\client_files\\brain_tumor_cnn_2025-12-21_16-10-58.pth"
    doc_id="6947d5c22ed956285d961d55"
    FL_Averaging(data_path=data_path, path_model=model_path, doc_id=doc_id)
    