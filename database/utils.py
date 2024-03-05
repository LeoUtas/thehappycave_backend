from fastapi import UploadFile, HTTPException
from firebase_admin import firestore, storage
from fastapi.concurrency import run_in_threadpool


async def upload_messages_to_firebase(
    audio_file: UploadFile, ID: str, source: str, date: str, text: str, userUID: str
):
    try:
        # Upload audio file to Firebase Storage
        bucket = await run_in_threadpool(
            storage.bucket
        )  # Assuming storage.bucket is a callable that returns a bucket object
        blob = bucket.blob(f"{source}/{ID}")

        # Read file content in async manner
        file_content = await audio_file.read()

        # Upload file using run_in_threadpool to not block the event loop
        await run_in_threadpool(
            blob.upload_from_string, file_content, content_type=audio_file.content_type
        )

        # Make the blob public - consider doing this in a more secure way
        await run_in_threadpool(blob.make_public)

        # Save metadata in Firestore
        db = firestore.client()

        if source == "openai":
            doc_reference = db.collection("openaiMessages").document(ID)
        else:
            doc_reference = db.collection("userMessages").document(ID)

        # Firestore operations in threadpool
        await run_in_threadpool(
            doc_reference.set,
            {
                "audio_url": blob.public_url,
                "ID": ID,
                "source": source,
                "date": date,
                "text": text,
                "userUID": userUID,
            },
        )

        return blob.public_url
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to upload message: {str(e)}"
        )
