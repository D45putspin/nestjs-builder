#!/usr/bin/env python3
import os
import subprocess

def create_file(path, content=""):
    with open(path, "w") as file:
        file.write(content)

def main():
  
    name = input("Enter the name of the entity (module): ").capitalize()
    lowercase_name = name.lower()

 
    base_path = os.path.join(os.getcwd(), lowercase_name)
    graphql_path = os.path.join(base_path, "graphql")
    os.makedirs(graphql_path, exist_ok=True)

    create_file(
        os.path.join(graphql_path, f"{lowercase_name}.graphql"),
        f"""scalar Date

type {name} {{
  _id: ID!
  
}}

input Create{name}Input {{
 name:String
}}

input Update{name}Input {{
name:String
}}

type Mutation {{
  create{ name }(input: Create{ name }Input): { name }
  update{ name }(id: ID!, input: Update{ name }Input): { name }
  delete{ name }(id: ID!): Success
}}

type Query {{
  get{ name }(id: ID!): { name }
  list{ name }s: [{ name }]
}}

type Success {{
  success: Boolean
}}
"""
    )

    #  resolver file
    create_file(
        os.path.join(graphql_path, f"{lowercase_name}.resolver.ts"),
        f"""import {{ Query, Resolver, Mutation, Args }} from '@nestjs/graphql';
import {{ {name}Service }} from '../{lowercase_name}.service';
import {{ Create{name}Input, Update{name}Input }} from 'src/graphql/graphql-schema';

@Resolver("{name}")
export class {name}Resolver {{
  constructor(private readonly {lowercase_name}Service: {name}Service) {{}}

  @Query('get{ name }')
  async get{ name }(@Args('id') id: string) {{
    return this.{lowercase_name}Service.getById(id);
  }}

  @Query('list{ name }s')
  async list{ name }s() {{
    return this.{lowercase_name}Service.findAll();
  }}

  @Mutation( 'create{name}')
  async create{ name }(@Args('input') input: Create{name}Input) {{
    return this.{lowercase_name}Service.create(input);
  }}

  @Mutation('update{name}')
  async update{ name }(@Args('id') id: string, @Args('input') input: Update{name}Input) {{
    return this.{lowercase_name}Service.update(id, input);
  }}
}}
"""
    )

    #  model file
    create_file(
        os.path.join(base_path, f"{lowercase_name}.model.ts"),
        f"""import {{ ObjectType, Field, ID }} from '@nestjs/graphql';
export const {name}_MODEL = "AuthUsers";

@ObjectType()
export class {name}Schema {{
  @Field(() => ID)
  _id: string;

 
}}
"""
    )

    #  module file
    create_file(
        os.path.join(base_path, f"{lowercase_name}.module.ts"),
        f"""import {{ Module }} from '@nestjs/common';
import {{ MongooseModule }} from '@nestjs/mongoose';
import {{ {name}Schema, {name}_MODEL }} from './{lowercase_name}.model';
import {{ {name}Service }} from './{lowercase_name}.service';
import {{ {name}Resolver }} from './graphql/{lowercase_name}.resolver';

@Module({{
  imports: [
    MongooseModule.forFeature([{{ name: {name}_MODEL, schema: {name}Schema }}]),
  ],
  providers: [{name}Service, {name}Resolver],
  exports: [{name}Service],
}})
export class {name}Module {{}}
"""
    )

    # service file
    create_file(
        os.path.join(base_path, f"{lowercase_name}.service.ts"),
        f"""import {{ Injectable, NotFoundException }} from '@nestjs/common';
import {{ InjectModel }} from '@nestjs/mongoose';
import {{ Model }} from 'mongoose';
import {{ {name}Schema }} from './{lowercase_name}.model';
import {{ Create{name}Input, Update{name}Input }} from 'src/graphql/graphql-schema';

@Injectable()
export class {name}Service {{
  constructor(
    @InjectModel('{name}') private readonly {lowercase_name}Model: Model<{name}Schema>
  ) {{}}

  async create(input: Create{name}Input): Promise<{name}Schema> {{
    const created{ name } = new this.{lowercase_name}Model(input);
    return await created{ name }.save();
  }}

  async getById(id: string): Promise<{name}Schema> {{
    const {lowercase_name} = await this.{lowercase_name}Model.findById(id);
    if (!{lowercase_name}) {{
      throw new NotFoundException(`{name} with ID '{{id}}' not found`);
    }}
    return {lowercase_name};
  }}

  async findAll(): Promise<{name}Schema[]> {{
    return this.{lowercase_name}Model.find().exec();
  }}

  async update(id: string, input: Update{name}Input): Promise<{name}Schema> {{
    const updated{ name } = await this.{lowercase_name}Model.findByIdAndUpdate(id, input, {{ new: true }});
    if (!updated{ name }) {{
      throw new NotFoundException(`{name} with ID '{{id}}' not found`);
    }}
    return updated{ name };
  }}

  async delete(id: string): Promise<{{ success: boolean }}> {{
    const result = await this.{lowercase_name}Model.findByIdAndDelete(id);
    if (!result) {{
      throw new NotFoundException(`{name} with ID '{{id}}' not found`);
    }}
    return {{ success: true }};
  }}
}}
"""
    )

    print(f"Module '{name}' created with the following structure:")
    print(f"{base_path}/")
    print(f" ├── graphql/")
    print(f" │   ├── {lowercase_name}.graphql")
    print(f" │   └── {lowercase_name}.resolver.ts")
    print(f" ├── {lowercase_name}.model.ts")
    print(f" ├── {lowercase_name}.module.ts")
    print(f" └── {lowercase_name}.service.ts")

   
    try:
    
        os.chdir("..")
        print("Moved up to parent directory.")
        
      
        subprocess.run(["npx", "ts-node", "src/graphql/generate-typings.ts"], check=True)
        print("Ran 'npx ts-node src/graphql/generate-typings.ts'.")
        
       
        os.chdir("src")
        print("Returned to 'src' directory.")
        
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running the command: {e}")

if __name__ == "__main__":
    main()

