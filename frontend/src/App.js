import React from "react";
import "fomantic-ui-css/semantic.css";
import { Container, Header, Segment, Button } from "semantic-ui-react";
import JobContainer from "./JobContainer";

class App extends React.Component {
  state = {
    mode: "best",
    label: "unlabeled",
    time: "week",
  };

  ha;

  render() {
    return (
      <Container style={{ padding: "20px" }}>
        <Header as='h1'>Linkedin Job Recommender</Header>
        <Segment inverted>
          <Header as='h3' inverted>
            by Fábio Baldissera
          </Header>
        </Segment>
        <Button.Group>
          <Button
            onClick={() => this.setState({ mode: "best" })}
            active={this.state.mode == "best"}
          >
            Best
          </Button>
          <Button
            onClick={() => this.setState({ mode: "doubt" })}
            active={this.state.mode == "doubt"}
          >
            Doubt
          </Button>
          <Button
            onClick={() => this.setState({ mode: "worst" })}
            active={this.state.mode == "worst"}
          >
            Worst
          </Button>
        </Button.Group>
        <Button.Group style={{ marginLeft: "20px" }}>
          <Button
            onClick={() => this.setState({ label: "unlabeled" })}
            active={this.state.label == "unlabeled"}
          >
            Only Unlabeled
          </Button>
          <Button
            onClick={() => this.setState({ label: "all" })}
            active={this.state.label == "all"}
          >
            All
          </Button>
        </Button.Group>

        <Button.Group style={{ marginLeft: "20px" }}>
          <Button
            onClick={() => this.setState({ time: "week" })}
            active={this.state.time == "week"}
          >
            Last Week
          </Button>
          <Button
            onClick={() => this.setState({ time: "month" })}
            active={this.state.time == "month"}
          >
            Last Month
          </Button>
          <Button
            onClick={() => this.setState({ time: "all" })}
            active={this.state.time == "all"}
          >
            All
          </Button>
        </Button.Group>

        <JobContainer
          mode={this.state.mode}
          label={this.state.label}
          time={this.state.time}
        />
      </Container>
    );
  }
}
export default App;
