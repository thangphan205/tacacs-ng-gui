import {
  Button,
  ButtonGroup,
  DialogActionTrigger,
  Input,
  Text,
  VStack,
} from "@chakra-ui/react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useState } from "react"
import { type SubmitHandler, useForm } from "react-hook-form"
import { FaExchangeAlt } from "react-icons/fa"

import { type ApiError, type RulesetScriptSetPublic, RulesetscriptsetsService } from "@/client"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"
import {
  DialogBody,
  DialogCloseTrigger,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogRoot,
  DialogTitle,
  DialogTrigger,
} from "../ui/dialog"
import { Field } from "../ui/field"

interface EditRulesetScriptSetProps {
  rulesetscriptset: RulesetScriptSetPublic
}

interface RulesetScriptSetUpdateForm {
  key: string;
  value: string;
  description?: (string | null);
  rulesetscript_id: string;
}

const EditRulesetScriptSet = ({ rulesetscriptset }: EditRulesetScriptSetProps) => {
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast } = useCustomToast()
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<RulesetScriptSetUpdateForm>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      ...rulesetscriptset,
      description: rulesetscriptset.description ?? undefined,
    },
  })

  const mutation = useMutation({
    mutationFn: (data: RulesetScriptSetUpdateForm) =>
      RulesetscriptsetsService.updateRulesetscriptset({ id: rulesetscriptset.id, requestBody: data }),
    onSuccess: () => {
      showSuccessToast("RulesetScriptSet updated successfully.")
      reset()
      setIsOpen(false)
    },
    onError: (err: ApiError) => {
      handleError(err)
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["rulesetscriptsets"] })
    },
  })

  const onSubmit: SubmitHandler<RulesetScriptSetUpdateForm> = async (data) => {
    mutation.mutate(data)
  }

  return (
    <DialogRoot
      size={{ base: "xs", md: "md" }}
      placement="center"
      open={isOpen}
      onOpenChange={({ open }) => setIsOpen(open)}
    >
      <DialogTrigger asChild>
        <Button variant="ghost">
          <FaExchangeAlt fontSize="16px" />
          Edit RulesetScriptSet
        </Button>
      </DialogTrigger>
      <DialogContent>
        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogHeader>
            <DialogTitle>Edit RulesetScriptSet</DialogTitle>
          </DialogHeader>
          <DialogBody>
            <Text mb={4}>Update the item details below.</Text>
            <VStack gap={4}>
              <Field
                required
                invalid={!!errors.key}
                errorText={errors.key?.message}
                label="key"
              >
                <Input
                  {...register("key", {
                    required: "key is required",
                  })}
                  placeholder="key"
                  type="text"
                />
              </Field>
              <Field
                required
                invalid={!!errors.value}
                errorText={errors.value?.message}
                label="value"
              >
                <Input
                  {...register("value", {
                    required: "value is required",
                  })}
                  placeholder="value"
                  type="text"
                />
              </Field>
              <Field
                required
                invalid={!!errors.rulesetscript_id}
                errorText={errors.rulesetscript_id?.message}
                label="rulesetscript_id"
              >
                <Input
                  {...register("rulesetscript_id", {
                    required: "rulesetscript_id is required",
                  })}
                  placeholder="rulesetscript_id"
                  type="text"
                />
              </Field>
              <Field
                invalid={!!errors.description}
                errorText={errors.description?.message}
                label="Description"
              >
                <Input
                  {...register("description")}
                  placeholder="Description"
                  type="text"
                />
              </Field>
            </VStack>
          </DialogBody>

          <DialogFooter gap={2}>
            <ButtonGroup>
              <DialogActionTrigger asChild>
                <Button
                  variant="subtle"
                  colorPalette="gray"
                  disabled={isSubmitting}
                >
                  Cancel
                </Button>
              </DialogActionTrigger>
              <Button variant="solid" type="submit" loading={isSubmitting}>
                Save
              </Button>
            </ButtonGroup>
          </DialogFooter>
        </form>
        <DialogCloseTrigger />
      </DialogContent>
    </DialogRoot>
  )
}

export default EditRulesetScriptSet
