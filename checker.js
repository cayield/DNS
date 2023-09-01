const fs = require('fs').promises;
const dns = require('dns');

const resolverFile = 'dns_resolvers.txt';

async function testResolvers() {
  try {
    const data = await fs.readFile(resolverFile, 'utf8');
    const resolvers = Array.from(new Set(data.split('\n').filter(Boolean)));

    const workingResolvers = [];

    for (const resolver of resolvers) {
      const trimmedResolver = resolver.trim();
      try {
        await dns.promises.resolve('example.com', 'A', { resolver: trimmedResolver, timeout: 2000 });
        workingResolvers.push(trimmedResolver);
      } catch {
        continue;
      }
    }

    await fs.writeFile('working_dns_resolvers.txt', workingResolvers.join('\n'), 'utf8');
    console.log(`Found ${workingResolvers.length} working DNS resolvers.`);
  } catch (error) {
    console.error(error);
  }
}

testResolvers();
