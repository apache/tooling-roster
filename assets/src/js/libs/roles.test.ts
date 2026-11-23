import { describe, expect, it } from 'vitest';
import { describeRoles, roleName } from '@/js/libs/roles';

describe('roleName', () => {
  it('names each role the server grants', () => {
    expect(roleName('secretary')).toBe('Secretary');
    expect(roleName('admin')).toBe('Admin');
  });

  it('shows a role it does not know by its own name rather than dropping it', () => {
    expect(roleName('auditor')).toBe('auditor');
  });
});

describe('describeRoles', () => {
  it('says so when there is no role at all', () => {
    expect(describeRoles([])).toBe('no role in this tool');
  });

  it('joins two with "and" and more with commas', () => {
    expect(describeRoles(['secretary'])).toBe('Secretary');
    expect(describeRoles(['secretary', 'admin'])).toBe('Secretary and Admin');
    expect(describeRoles(['secretary', 'admin', 'auditor'])).toBe('Secretary, Admin and auditor');
  });
});
