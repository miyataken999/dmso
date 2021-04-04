import React from "react";
import { MemoryRouter } from "react-router-dom";

import App from "../App";

import axios from "axios";
import MockAdapter from "axios-mock-adapter"
import { mockPost, mockTag, mockCategory } from "./mockUtils";
import { withKnobs, text, boolean, number } from '@storybook/addon-knobs';

//export default {
//  title: 'Storybook Knobs',/
//  decorators: [withKnobs],
//};
// Add the `withKnobs` decorator to add knobs support to your stories.
// You can also configure `withKnobs` as a global decorator.

// Knobs for React props
export const withAButton = () => (
  <button disabled={boolean('Disabled', false)}>{text('Label', 'Hello Storybook')}</button>
);


export default {
  title: "App",
  component: App,
  decorators: [withKnobs],
};

export const Example = () => {
  const mock = new MockAdapter(axios);
  mockCategory(mock);
  mockPost(mock);
  mockTag(mock);

  return (
    <MemoryRouter initialEntries={["/1"]}>
      <App/>
    </MemoryRouter>
  );
};
