import dash_ag_grid as dag 

columnDefs = [
    {
        "headerName": "Company",  # Name of table displayed in app
        "field": "company",
        "maxWidth": 300,
        "minWidth": 100,
        "cellRenderer": "markdown",
        "cellRendererParams": {"className": "btn btn-light btn-sm", },
    },

    {
        "headerName": "Report",  # Name of table displayed in app
        "field": "markdownURL",
        "maxWidth": 200,
        "minWidth": 100,
        "linkTarget":"_blank",
        "cellRenderer": "markdown",
        "cellRendererParams": {"className": "btn btn-light btn-sm", },
    },

    #     {
    #     "headerName": "In Database",  # Name of table displayed in app
    #     "field": "inDatabase",
    #     "maxWidth": 200,
    #     "minWidth": 100,
    #     # "linkTarget":"_blank",
    #     "cellRenderer": "Checkbox",
    #     },

    #     {
    #     "headerName": "Add to AI",
    #     "field": "addButton",
    #     "maxWidth": 150,
    #     "minWidth": 150,
    #     "cellRenderer": "Button",
    #     "cellRendererParams": {"className": "btn btn-info"},
    # },
                
    {
        "headerName": "Filing Date",
        "field": "filingDate",
        "linkTarget":"_blank",
        "cellRenderer": "markdown",
        "cellRendererParams": {"className": "btn btn-light btn-sm"},

    },
    
    {
        "headerName": "Report Year",
        "field": "reportYear",
        "linkTarget":"_blank",
        "cellRenderer": "markdown",
        "cellRendererParams": {"className": "btn btn-light btn-sm"},
    },


]

defaultColDef = {
    "filter": True,
    "floatingFilter": False,
    "resizable": True,
    "sortable": True,
    "editable": True,

}

table = dag.AgGrid(
    id="table-id",
    # className="ag-theme-alpine-dark",
    columnDefs=columnDefs,
    rowData=[],
    columnSize="sizeToFit",
    defaultColDef=defaultColDef,
    dashGridOptions={"undoRedoCellEditing": True, "rowSelection":"multiple"},
)


