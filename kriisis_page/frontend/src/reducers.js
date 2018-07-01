import { combineReducers } from 'redux';

import title from './ducks/title';
import categories from './ducks/categories';
import shops from './ducks/shops';

const rootReducer = combineReducers({
  title,
  categories,
  shops,
});

export default rootReducer;
