📦 Order Tracking and Management System
This project, built with Django (Python), aims to digitize the order tracking process made by clients.
.

🚀 Main Features

Order lifecycle management:

A client places an order.

The order is automatically assigned to a sales representative using a Round Robin algorithm.

The sales rep can accept or reject the order.

If accepted, a technician is assigned to prepare the order.

Once prepared, the order goes through the statuses shipped → delivered.

After delivery, the technician installs the order.

When the installation is marked as completed, the sales rep finalizes the order.

The client can leave feedback on the order.

Order cancellation: the client can cancel the order at any time except when it has the status installed, delivered, or finalized.

Intervention files: each system actor can upload/download a report file for their intervention. These files are visible to the administrator.

Discount PDF generation: upon placing an order, the client can generate and download a discount PDF.

Data migration: integration with Pandas to migrate existing data from Excel files into the database.

CRUD operations: full Create, Read, Update, Delete features on:

Materials

Human Resources (HR)

🛠️ Tech Stack

Backend: Django (Python)

Database: (MYsql)

Data Processing: Pandas

PDF Export: ReportLab 