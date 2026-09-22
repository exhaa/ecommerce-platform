from app.celery_app import celery
from reportlab.pdfgen import canvas
from pathlib import Path
@celery.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3},
    retry_backoff=True
)
def generate_invoice_pdf(self, order_id, user_id, total_amount):

    try:
    
        output_dir = Path("generated_invoices")
        output_dir.mkdir(exist_ok=True)

        file_path = output_dir / f"invoice_{order_id}.pdf"

        pdf = canvas.Canvas(str(file_path))

        pdf.setTitle(f"Invoice {order_id}")

        pdf.drawString(100, 750, "E-Commerce Invoice")
        pdf.drawString(100, 720, f"Order ID: {order_id}")
        pdf.drawString(100, 690, f"User ID: {user_id}")
        pdf.drawString(100, 660, f"Total Amount: {total_amount}")
        pdf.drawString(100, 620, "Thank you for your purchase!")

        pdf.save()

        print(f"Invoice generated: {file_path}")

        return str(file_path)

    except Exception as exc:

        if self.request.retries >= 3:
            from app.tasks.dlq_tasks import save_failed_task

            save_failed_task.delay(
                "generate_invoice_pdf",
                str(self.request.args),
                str(exc)
            )

        raise