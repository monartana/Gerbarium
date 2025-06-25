from math import ceil

from sqlalchemy import or_, inspect
from sqlalchemy import desc, asc
from typing import Optional


def paginate(query, page: int = 1, page_size: int = 10):
    total_items = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()

    return items, total_items


def search_and_sort(db,
                    model,
                    search_query: Optional[str] = None,
                    sort_by: Optional[str] = None,
                    page: int = 1,
                    page_size: int = 10,
                    sort_direction="asc"):
    query = db.query(model)

    if search_query:
        search_filter = or_(
            *[getattr(model, c.name).contains(search_query) for c in inspect(model).columns])
        query = query.filter(search_filter)

    if sort_by:
        if hasattr(model, sort_by):
            query = query.order_by(
                desc(getattr(model, sort_by))
                if sort_direction == 'desc'
                else asc(getattr(model, sort_by))
            )
        else:
            raise ValueError(f"Invalid sort field: {sort_by}")

    items, total_items = paginate(query, page=page, page_size=page_size)

    return {"items": items, "total_pages": ceil(total_items / page_size), "current_page": page}
