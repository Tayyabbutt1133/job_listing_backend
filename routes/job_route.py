from flask import Blueprint, request, jsonify
from models.jobs import Job
from db import db
from sqlalchemy import func
from Scraper.scrape import scrape_actuary_jobs

# Mini app/routes for Job listing only
job_bp = Blueprint("jobs", __name__)


@job_bp.route("/jobs", methods=["GET"])
def get_jobs():
    try:
        query = Job.query

        # Get params safely & normalize
        locations = [loc.lower() for loc in request.args.getlist("locations")]
        job_types = [jt.lower() for jt in request.args.getlist("jobTypes")]
        post_scope = request.args.get("postscope", "").lower()
        print(post_scope)
        filters = []
        if locations:
            filters.append(func.lower(Job.location).in_(locations))
        if job_types:
            filters.append(func.lower(Job.job_type).in_(job_types))

        if filters:
            query = query.filter(*filters)

        # Sorting
        print("Post scope value before changing order :", post_scope)
        if post_scope == "newest":
            print("Newest condition wins")
            query = query.order_by(Job.posting_date.desc())
        elif post_scope == "oldest":
            print("Oldest condition wins")
            query = query.order_by(Job.posting_date.asc())


        jobs = query.all()
        print("Query results from database : ", jobs)

        jobs_list = [
            {
                "id": j.id,
                "title": j.title,
                "company": j.company,
                "location": j.location,
                "date": j.posting_date.strftime("%Y-%m-%d"),
                "job_type": j.job_type,
                "tags": j.tags,
            }
            for j in jobs
        ]

        return jsonify({"message": "Success", "data": jobs_list}), 200

    except Exception as e:
        print(f"Error fetching jobs: {e}")
        return jsonify({"error": "Failed to fetch jobs"}), 500


@job_bp.route("/jobs/<int:job_id>", methods=["GET"])
def get_job(job_id):
    try:
        job = Job.query.get(job_id)  # fetch by primary key

        if not job:
            return jsonify({"error": "Job not found"}), 404

        job_data = {
            "id": job.id,
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "posting_date": job.posting_date,
            "job_type": job.job_type,
            "tags": job.tags,
        }

        return jsonify(job_data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@job_bp.route("/jobs", methods=["POST"])
def create_job():
    try:
        data = request.get_json()
        new_job = Job(
            title=data["title"].capitalize(),
            company=data["company"].capitalize(),
            location=data["location"].capitalize(),
            posting_date=data.get("posting_date"),
            job_type=data["job_type"].capitalize(),
            tags=data.get("tags").capitalize() if data.get("tags") else None,
        )

        db.session.add(new_job)
        db.session.commit()
        return jsonify({"message": "User created successfully", "id": new_job.id}), 200
    except Exception as e:
        print(f"Error saving jobs: {e}")
        return jsonify({"error": "Failed to Save New Job"}), 500


@job_bp.route("/jobs/<int:job_id>", methods=["PUT"])
def update_job(job_id):
    try:
        job = Job.query.get(job_id)
        if not job:
            return jsonify({"error": "Job not found"}), 404

        data = request.get_json()
        job.title = data.get("title", job.title)
        job.company = data.get("company", job.company)
        job.location = data.get("location", job.location)
        job.posting_date = data.get("date", job.posting_date)
        job.job_type = data.get("jobType", job.job_type)
        job.tags = data.get("tags", job.tags)

        db.session.commit()
        return jsonify({"message": "Job updated successfully"}), 200

    except Exception as e:
        print(f"Error updating job: {e}")
        return jsonify({"error": "Failed to update job"}), 500


@job_bp.route("/jobs/<int:job_id>", methods=["DELETE"])
def delete_job(job_id):

    try:
        job = Job.query.get(job_id)
        if not job:
            return jsonify({"error": "Job not found"}), 404

        db.session.delete(job)
        db.session.commit()
        return jsonify({"message": "Job deleted successfully"}), 200

    except Exception as e:
        print(f"Error deleting job: {e}")
        return jsonify({"error": "Failed to delete job"}), 500

@job_bp.route("/scrape", methods=["GET"])
def scrape_jobs():
    scrape_actuary_jobs()
    return {"message": "Scraping completed!"}, 200

