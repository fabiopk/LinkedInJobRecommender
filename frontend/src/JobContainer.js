import React, { Component } from "react";
import JobTable from "./JobTable";
import axios from "./axiosApi";

export default class JobContainer extends Component {
  state = {
    jobs: [],
    page: 0,
  };

  header = [
    "Label",
    "Title",
    "Company",
    "Location",
    "Seniority",
    "Description",
    "Action",
    "Score",
  ];

  componentDidMount() {
    this.handlePageClick = this.handlePageClick.bind(this);
    this.handleSetLabel = this.handleSetLabel.bind(this);
    this.fetchData = this.fetchData.bind(this);

    this.fetchData();
  }

  componentDidUpdate(prevProps) {
    if (
      prevProps.mode !== this.props.mode ||
      prevProps.label !== this.props.label ||
      prevProps.time !== this.props.time
    ) {
      this.fetchData();
    }
  }

  fetchData() {
    axios
      .get("/preds", {
        params: {
          start: 0,
          mode: this.props.mode,
          label: this.props.label,
          time: this.props.time,
        },
        timeout: 2000,
      })
      .then((res) => {
        const { result } = res.data;
        this.setState({ jobs: result });
      });
  }

  handlePageClick(page) {
    this.setState({ page });
  }

  handleSetLabel(job, label) {
    const newJobs = this.state.jobs.map((j) => {
      if (j.jobId == job.jobId) {
        j.label = label;
      }
      return j;
    });
    this.setState({ jobs: newJobs });
    axios.put(`/preds/${job.jobId}`, { label }).then((res) => {
      console.log(res);
    });
  }

  render() {
    return (
      <JobTable
        header={this.header}
        rows={this.state.jobs.slice(
          this.state.page * 15,
          (this.state.page + 1) * 15
        )}
        onPageClick={this.handlePageClick}
        onSetLabel={this.handleSetLabel}
        numPages={parseInt(this.state.jobs.length / 15)}
        page={this.state.page}
      />
    );
  }
}
